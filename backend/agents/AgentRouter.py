import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from agents.ehall_agent import EhallAgent
from agents.budget_agent import BudgetAgent
from agents.health_agent import HealthAgent
from agents.travel_agent import TravelAgent
from agents.intent_classifier import IntentClassifier
from thread_local import set_current_username

class AgentRouter:
    """Agent 路由器"""
    
    INTENT_TO_AGENT = {
        "budget_query": "budget",
        "budget_action": "budget",
        "health_query": "health",
        "health_action": "health",
        "travel_query": "travel",
        "travel_action": "travel",
        "ehall_query": "ehall",
        "general": "ehall",  # 默认使用教务Agent
    }
    
    def __init__(self):
        self.classifier = IntentClassifier()
        
        kb_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "通识选课2.csv")

        # 初始化各个 Agent
        self.agents = {
            "ehall": EhallAgent(verbose=False, knowledge_base_path=kb_path),
            "budget": BudgetAgent(verbose=False),
            "health": HealthAgent(verbose=False),
            "travel": TravelAgent(verbose=False)
        }
    
    def route(self, user_message: str, user_id: str, chat_history: list = None) -> str:
        """
        路由并调用合适的 Agent
        
        Args:
            user_message: 用户消息
            user_id: 用户ID
            chat_history: 对话历史
        
        Returns:
            Agent 的响应内容
        """
        
        # 1. 意图识别
        history_str = self._format_history(chat_history)
        intent_result = self.classifier.classify(user_message, history_str)
        
        intent = intent_result.get("intent", "general")
        confidence = intent_result.get("confidence", 0.5)
        
        print(f"意图识别结果: {intent} (置信度: {confidence})")
        
        # 2. 选择 Agent
        agent_name = self.INTENT_TO_AGENT.get(intent, "ehall")
        
        # 3. 调用 Agent
        agent = self.agents.get(agent_name)
        
        if agent:
            set_current_username(user_id)
            response = agent.run(
                user_input=user_message,
                chat_history=chat_history or []
            )
            return response
        else:
            return "抱歉，暂时无法处理您的请求。"
    
    def _format_history(self, chat_history: list) -> str:
        """格式化对话历史"""
        if not chat_history:
            return ""
        
        lines = []
        for msg in chat_history[-5:]:  # 只取最近5条
            role = "用户" if msg.get("role") == "user" else "助手"
            content = msg.get("content", "")
            lines.append(f"{role}: {content}")
        
        return "\n".join(lines)

if __name__ == "__main__":
    router = AgentRouter()
    user_message = "我是 2023001，我想查看我的健康统计"
    response = router.route(user_message, user_id="2023001")
    print(f"Agent 响应: {response}")