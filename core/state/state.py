# core/state/state.py

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConversationState:
    """
    Состояние одного диалога / пользователя.

    Хранит:
    - историю сообщений
    - результаты агентов
    - произвольный context
    """

    # OpenAI/Groq messages format
    messages: list[dict] = field(default_factory=list)

    # результаты работы агентов
    # example:
    # {
    #     "researcher_agent": "...",
    #     "math_agent": "..."
    # }
    agent_results: dict[str, Any] = field(default_factory=dict)

    # дополнительный runtime context
    # example:
    # {
    #     "current_topic": "...",
    #     "language": "ru"
    # }
    context: dict[str, Any] = field(default_factory=dict)

    # metadata диалога
    metadata: dict[str, Any] = field(default_factory=dict)

    # ---------------- MESSAGES ----------------

    def add_user_message(self, content: str):
        self.messages.append({
            "role": "user",
            "content": content
        })

    def add_assistant_message(self, content: str):
        self.messages.append({
            "role": "assistant",
            "content": content
        })

    def add_system_message(self, content: str):
        self.messages.append({
            "role": "system",
            "content": content
        })

    def add_tool_message(
        self,
        tool_call_id: str,
        content: str
    ):
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": content
        })

    # ---------------- AGENT RESULTS ----------------

    def set_agent_result(
        self,
        agent_name: str,
        result: Any
    ):
        self.agent_results[agent_name] = result

    def get_agent_result(
        self,
        agent_name: str
    ) -> Any:
        return self.agent_results.get(agent_name)

    # ---------------- CONTEXT ----------------

    def set_context(
        self,
        key: str,
        value: Any
    ):
        self.context[key] = value

    def get_context(
        self,
        key: str,
        default=None
    ):
        return self.context.get(key, default)

    # ---------------- UTIL ----------------

    def clear_messages(self):
        self.messages.clear()

    def clear_agent_results(self):
        self.agent_results.clear()

    def reset(self):
        """
        Полный сброс состояния диалога.
        """
        self.messages.clear()
        self.agent_results.clear()
        self.context.clear()
        self.metadata.clear()