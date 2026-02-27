# 文件: backend/agents/budget_agent.py
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
    
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from config import config
from tools.budget_tools import get_expenses, get_budget_stats, add_expense, set_budget

class BudgetAgent:
    def __init__(self, verbose=True):
        self.llm = self._initialize_llm()
        self.tools = [get_expenses, get_budget_stats, add_expense, set_budget]
        self.prompt = self._create_prompt()
        self.agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=verbose)
    
    def _initialize_llm(self) -> ChatDeepSeek:
        """初始化大语言模型 - 使用DeepSeek模型"""
        return ChatDeepSeek(
            model="deepseek-chat",
            temperature=0,
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL,
        )

    def _create_prompt(self):
        template = """
        你是一个专业的预算管家助手，擅长理财和消费分析。
        你可以帮助用户：
        1. 记录消费（使用 add_expense 工具）
        2. 查询消费记录（使用 get_expenses 工具）
        3. 查看预算统计（使用 get_budget_stats 工具）
        4. 设置月度预算（使用 set_budget 工具）
        
        请用清晰、友好的方式回答用户问题。
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
    agent = BudgetAgent(verbose=True)
    user_input = "我这个月的消费记录是什么？"
    response = agent.run(user_input)
    print(response)
