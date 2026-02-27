import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from config import config
from tools.health_tools import health_checkin, get_health_records, get_health_stats


class HealthAgent:
    def __init__(self, verbose=True):
        self.llm = self._initialize_llm()
        self.tools = [health_checkin, get_health_records, get_health_stats]
        self.prompt = self._create_prompt()
        self.agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=verbose)
    
    def _initialize_llm(self) -> ChatDeepSeek:
        return ChatDeepSeek(
            model="deepseek-chat",
            temperature=0,
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL,
        )
    
    def _create_prompt(self):
        template = """
        你是一个专业的健康顾问助手，擅长健康数据分析和生活方式建议。
        你可以帮助用户：
        1. 健康打卡（使用 health_checkin 工具）- 记录睡眠、运动、步数、健康状态、体重等
        2. 查询健康记录（使用 get_health_records 工具）- 查看历史打卡数据
        3. 健康统计（使用 get_health_stats 工具）- 分析睡眠、运动、步数等统计数据
        
        请用清晰、友好的方式回答用户问题。
        如果用户要打卡，请引导用户提供必要信息（学号、日期、运动情况等）。
        如果用户要查看统计数据，可以默认查询30天，也可指定天数。
        """
        return ChatPromptTemplate.from_messages([
            ("system", template),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad")
        ])
    
    def run(self, user_input: str, chat_history: list = None):
        result = self.executor.invoke({
            "input": user_input,
            "chat_history": chat_history or []
        })
        return result["output"]


if __name__ == "__main__":
    agent = HealthAgent(verbose=True)
    response = agent.run("我是2023001，想查看我的健康统计")
    print(response)
