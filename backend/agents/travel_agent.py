import json
import os
import sys
import requests
from datetime import datetime, timedelta
from typing import List, Dict
# 自动化抓取工具
# from drissionpage import ChromiumPage, ChromiumOptions

# 更安全的路径处理方式
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)  # 使用insert(0)确保优先搜索

# LangChain 核心
from langchain_deepseek import ChatDeepSeek
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 假设这些是从你的本地文件导入的
from tools.travel_tools import save_trip 
from config import config

# ==========================================
# 1. 核心 Tool 函数定义
# ==========================================

@tool
def fetch_xhs_intel(keyword: str) -> str:
    """
    从小红书抓取真实旅游攻略和避雷点。
    输入：目的地+关键词（如：上海 旅游 避雷）
    """
    # co = ChromiumOptions().set_headless(True) 
    # page = ChromiumPage(co)
    # try:
    #     search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes"
    #     page.get(search_url)
    #     page.wait(2) # 增加等待时间确保渲染
        
    #     items = page.eles('.note-item')[:5]
    #     intel_list = []
    #     for item in items:
    #         title = item.ele('.title').text if item.ele('.title') else "无标题笔记"
    #         intel_list.append(f"- {title}")
        
    #     content = "\n".join(intel_list) if intel_list else "未找到相关热门笔记"
    #     return f"【小红书实时情报】：\n{content}\n注意：优先关注评论区提到的近期施工、限流及季节性建议。"
    # except Exception as e:
    #     return f"小红书抓取失败: {str(e)}"
    # finally:
    #     page.quit()
    return "【小红书实时情报】：\n- 示例笔记1：上海武康路拍照攻略\n- 示例笔记2：上海旅游避雷指南\n注意：请实际运行时启用爬虫代码获取最新数据。"

@tool
def get_amap_data(spot_name: str, city: str) -> str:
    """
    获取高德地图精确POI信息。
    返回：地址、评分、营业时间、及一键导航链接。
    """
    # 建议通过 config.AMAP_KEY 获取
    AMAP_KEY = config.AMAP_KEY 
    url = "https://restapi.amap.com/v3/poi/text"
    params = {
        "key": AMAP_KEY,
        "keywords": spot_name,
        "city": city,
        "extensions": "all",
        "output": "json"
    }
    try:
        r = requests.get(url, params=params, timeout=5).json()
        if r.get('status') == '1' and r.get('pois'):
            poi = r['pois'][0]
            loc = poi['location']
            nav_url = f"https://uri.amap.com/marker?position={loc}&name={spot_name}&coordinate=gaode&callnative=1"
            
            info = {
                "name": poi['name'],
                "address": f"{poi['pname']}{poi['cityname']}{poi['adname']}{poi.get('address','')}",
                "rating": poi.get('biz_ext', {}).get('rating', '4.0'),
                "hours": poi.get('business_area', '见地图详情'),
                "nav_link": nav_url,
                "payment": "支持移动支付"
            }
            return json.dumps(info, ensure_ascii=False)
        return f"高德地图未找到 '{spot_name}' 的数据，请核实名称。"
    except Exception as e:
        return f"地图 API 调用失败: {str(e)}"

# ==========================================
# 2. TravelAgent 类定义
# ==========================================

class TravelAgent:
    def __init__(self, verbose=True):
        # 初始化模型 (确保 config.OPENAI_API_KEY 已配置)
        self.llm = self._initialize_llm()
        # 整合你提供的所有工具
        # 注意：save_trip 需要根据你之前的定义导入
        self.tools = [fetch_xhs_intel, get_amap_data, save_trip]
        self.prompt = self._create_prompt()
        
        # 创建 Tool Calling Agent
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.executor = AgentExecutor(
            agent=self.agent, 
            tools=self.tools, 
            verbose=verbose,
            handle_parsing_errors=True # 增强解析容错
        )
    
    def _initialize_llm(self) -> ChatDeepSeek:
        """初始化大语言模型 - 使用DeepSeek模型"""
        return ChatDeepSeek(
            model="deepseek-chat",
            temperature=0,
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL,
        )
    
    def _create_prompt(self):
        system_template = """你是一个专业的旅游规划师。
        你的目标是为用户提供极其精准且具备落地能力的旅行方案。
        
        你的工作流如下：
        1. **信息确认**：必须确认：目的地、天数、预算、出发时间、用户ID（学号）。
        2. **情报搜集**：调用 `fetch_xhs_intel` 搜索最新的避雷建议和热门机位。
        3. **地理校准**：每个推荐地点必须调用 `get_amap_data` 获取评分和 [🚗 高德导航] 链接。
        4. **规划行程**：生成结构化的 Markdown 行程，包含地址、评分、导航链接及支付说明。
        5. **持久化**：确认方案后，调用 `save_trip` 保存到数据库。

        注意：严禁虚构景点。如果高德地图查不到，请不要将其列入行程。"""
        
        return ChatPromptTemplate.from_messages([
            ("system", system_template),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
    
    def run(self, user_input: str, chat_history: list = None):
        result = self.executor.invoke({
            "input": user_input,
            "chat_history": chat_history or []
        })
        return result["output"]

# ==========================================
# 3. 运行示例
# ==========================================
if __name__ == "__main__":
    # 实例化 Agent
    travel_bot = TravelAgent(verbose=True)
    
    # 测试输入
    user_query = "我是2023001，我想5月1号去上海玩2天，预算2500元。重点想去武康路拍照。"
    
    # 实际运行
    response = travel_bot.run(user_query)
    print(response)