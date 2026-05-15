# researcher_agent.py
import json
from typing import List, Dict, Any, Optional

# Убедитесь, что класс GroqLLM доступен (можно через импорт из вашего модуля)
# from groq_llm import GroqLLM
# from search_tool import TavilySearchTool

class ResearcherAgent:
    """
    Субагент-исследователь, использующий GroqLLM и поисковый инструмент Tavily.
    """

    def __init__(self, llm: 'GroqLLM', search_tool: 'TavilySearchTool', max_iterations: int = 3):
        self.llm = llm
        self.search_tool = search_tool
        self.max_iterations = max_iterations

        # Устанавливаем системный промпт
        system_prompt = (
            "Ты — ИИ-исследователь. Твоя задача — собирать актуальную информацию из интернета.\n"
            "У тебя есть инструмент 'tavily_search'. Если тебе нужны свежие данные, вызови этот инструмент, передав поисковый запрос.\n"
            "Когда получишь результаты, проанализируй их и дай пользователю полный, структурированный ответ.\n"
            "Не выдумывай информацию, всегда опирайся на результаты поиска.\n"
            "Не вызывай один и тот же поисковый запрос повторно. Если информация не найдена, сообщи об этом."
        )
        self.llm.set_system_prompt(system_prompt)

        # Описание инструмента для GroqLLM
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "tavily_search",
                    "description": "Выполняет поиск в интернете по заданному запросу и возвращает релевантные результаты.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Поисковый запрос, например 'последние достижения квантовых вычислений 2025'"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
        self.llm.tools = self.tools

    async def research(self, query: str) -> str:
        """Главный метод: принимает вопрос, возвращает готовый исследовательский ответ."""
        iteration_count = 0
        last_calls = []   # защита от повторных вызовов

        current_input = query

        while iteration_count < self.max_iterations:
            iteration_count += 1
            response = await self.llm.call(current_input)

            # Если LLM вернула список tool_calls (как в GroqLLM)
            if isinstance(response, list) and response and "tool_calls" in response[0]:
                tool_calls = response
                if not tool_calls:
                    return "Не удалось обработать запрос исследователя."

                for tool_call in tool_calls:
                    func_name = tool_call.get("function", {}).get("name")
                    arguments = json.loads(tool_call.get("function", {}).get("arguments", "{}"))

                    # Проверка на повтор
                    call_key = (func_name, frozenset(arguments.items()))
                    if call_key in last_calls:
                        return f"Обнаружен повторный вызов {func_name} с теми же аргументами. Исследование прервано."
                    last_calls.append(call_key)

                    if func_name == "tavily_search":
                        search_query = arguments.get("query")
                        if not search_query:
                            observation = "Ошибка: не указан поисковый запрос."
                        else:
                            observation = await self.search_tool.search(search_query)
                    else:
                        observation = f"Неизвестный инструмент: {func_name}"

                    # Добавляем результат в историю LLM как сообщение tool
                    self.llm.history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.get("id"),
                        "content": observation
                    })

                # После выполнения всех вызовов продолжаем цикл с пустым вводом
                current_input = ""
                continue

            # Если ответ — строка (финальный текст)
            elif isinstance(response, str):
                return response.strip()

            else:
                return f"Неожиданный ответ от LLM: {response}"

        return "Исследование достигло максимального числа шагов и не завершилось. Попробуйте упростить запрос."
