from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import config

class IntentClassifier:
    """AI 意图分类器"""
    
    PROMPT_TEMPLATE = """
    你是一个意图分类助手。根据用户消息，判断用户想要使用哪个功能。
    
    可选意图类型：
    - budget_query: 询问预算、消费、支出相关信息
    - budget_action: 记录消费、设置预算等操作
    - health_query: 询问健康、打卡、运动相关信息
    - health_action: 健康打卡操作
    - travel_query: 询问旅行、行程相关信息
    - travel_action: 创建旅行计划操作
    - ehall_query: 教务相关（课表、成绩、选课等）
    - general: 通用对话（问候、闲聊等）
    
    对话历史：
    {chat_history}
    
    当前消息：{user_message}
    
    请直接输出以下格式的 JSON，不要有其他内容：
    {{"intent": "意图类型", "confidence": 0.95}}
    
    confidence 表示置信度，0-1 之间。
    """
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.prompt = ChatPromptTemplate.from_template(self.PROMPT_TEMPLATE)
    
    def _initialize_llm(self) -> ChatDeepSeek:
        """初始化大语言模型 - 使用DeepSeek模型"""
        return ChatDeepSeek(
            model="deepseek-chat",
            temperature=0,
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL,
        )
    
    def classify(self, user_message: str, chat_history: str = "") -> dict:
        """识别用户意图"""
        
        # 快速关键词匹配（可选，作为 fallback）
        keyword_intent = self._keyword_match(user_message)
        if keyword_intent:
            return keyword_intent
        
        # AI 分类
        try:
            response = self.llm.invoke(
                self.prompt.format(
                    chat_history=chat_history,
                    user_message=user_message
                )
            )
            
            import json
            # 尝试解析 JSON
            result = json.loads(response.content)
            return result
            
        except Exception as e:
            print(f"意图识别失败: {e}")
            return {"intent": "general", "confidence": 0.5}
    
    def _keyword_match(self, text: str) -> dict:
        """关键词快速匹配"""
        text = text.lower()
        
        budget_keywords = ["钱", "花费", "支出", "预算", "消费", "记账", "多少钱", "花了"]
        health_keywords = ["健康", "打卡", "身体", "睡眠", "运动", "步数", "体重"]
        travel_keywords = ["旅游", "旅行", "行程", "目的地", "去玩", "规划"]
        ehall_keywords = ["课表", "成绩", "选课", "教室", "评教", "培养方案"]
        
        for kw in budget_keywords:
            if kw in text:
                action = "budget_action" if any(x in text for x in ["记", "添加", "设置", "新增"]) else "budget_query"
                return {"intent": action, "confidence": 0.9, "source": "keyword"}
        
        for kw in health_keywords:
            if kw in text:
                action = "health_action" if any(x in text for x in ["打卡", "记录"]) else "health_query"
                return {"intent": action, "confidence": 0.9, "source": "keyword"}
        
        for kw in travel_keywords:
            if kw in text:
                action = "travel_action" if any(x in text for x in ["规划", "生成", "创建"]) else "travel_query"
                return {"intent": action, "confidence": 0.9, "source": "keyword"}
        
        for kw in ehall_keywords:
            if kw in text:
                return {"intent": "ehall_query", "confidence": 0.9, "source": "keyword"}
        
        return None
