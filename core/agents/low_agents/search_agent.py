# core/agents/researcher_agent/researcher_agent.py

import json

from core.state.state import ConversationState


class SearchAgent:
    """
    Агент-исследователь.

    Использует:
    - LLM
    - Tavily search tool
    - ConversationState
    """

    SYSTEM_PROMPT = (
        "Ты — ИИ-исследователь. "
        "Твоя задача — собирать актуальную информацию из интернета.\n"
        "У тебя есть инструмент 'tavily_search'. "
        "Если нужны свежие данные — используй его.\n"
        "После получения результатов дай структурированный ответ.\n"
        "Не выдумывай информацию.\n"
        "Не вызывай одинаковый поисковый запрос повторно."
    )

    def __init__(
        self,
        llm,
        search_tool,
        max_iterations: int = 3
    ):
        self.llm = llm
        self.search_tool = search_tool
        self.max_iterations = max_iterations

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "tavily_search",
                    "description": (
                        "Выполняет поиск в интернете "
                        "и возвращает релевантные результаты."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Поисковый запрос"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    async def research(
        self,
        query: str,
        state: ConversationState
    ) -> str:

        last_calls = set()

        # system prompt
        if not state.messages:
            state.add_system_message(
                self.SYSTEM_PROMPT
            )

        # user message
        state.add_user_message(query)

        for _ in range(self.max_iterations):

            response = await self.llm.call(
                messages=state.messages,
                tools=self.tools
            )

            # ---------------- ERROR ----------------

            if response["type"] == "error":
                return f"LLM error: {response['content']}"

            # ---------------- TOOL CALLS ----------------

            if response["type"] == "tool_calls":

                tool_calls = response["content"]

                for tool_call in tool_calls:

                    function_data = tool_call["function"]

                    func_name = function_data["name"]

                    arguments = json.loads(
                        function_data.get(
                            "arguments",
                            "{}"
                        )
                    )

                    # защита от повторов
                    call_key = (
                        func_name,
                        frozenset(arguments.items())
                    )

                    if call_key in last_calls:
                        return (
                            "Обнаружен повторный "
                            "вызов инструмента."
                        )

                    last_calls.add(call_key)

                    # -------- tavily search --------

                    if func_name == "tavily_search":

                        search_query = arguments.get("query")

                        if not search_query:
                            observation = (
                                "Ошибка: пустой поисковый запрос."
                            )
                        else:
                            observation = await self.search_tool.search(
                                search_query
                            )

                    else:
                        observation = (
                            f"Неизвестный инструмент: {func_name}"
                        )

                    # сохраняем вызов assistant
                    state.messages.append({
                        "role": "assistant",
                        "tool_calls": [tool_call]
                    })

                    # сохраняем tool result
                    state.add_tool_message(
                        tool_call_id=tool_call["id"],
                        content=observation
                    )

                continue

            # ---------------- FINAL TEXT ----------------

            if response["type"] == "text":

                final_text = response["content"]

                state.add_assistant_message(
                    final_text
                )

                state.set_agent_result(
                    "researcher_agent",
                    final_text
                )

                return final_text

        return (
            "Исследование достигло лимита "
            "итераций."
        )