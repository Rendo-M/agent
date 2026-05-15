import json
import asyncio
from typing import List, Dict, Any, Optional
from tavily import AsyncTavilyClient  # pip install tavily-python

# Предполагаем, что ваш класс GroqLLM находится в отдельном файле
# from groq_llm import GroqLLM

class TavilySearchTool:
    """Поисковый инструмент на основе Tavily API (асинхронный)."""
    def __init__(self, api_key: str):
        self.client = AsyncTavilyClient(api_key=api_key)

    async def search(self, query: str, max_results: int = 5) -> str:
        """
        Выполняет поиск и возвращает строку с результатами, готовую для LLM.
        """
        try:
            response = await self.client.search(
                query=query,
                search_depth="basic",   # "basic" или "advanced" (требует больше кредитов)
                max_results=max_results,
                include_answer=True,    # Tavily может вернуть краткий ответ
                include_raw_content=False
            )
            # Форматируем результат в читаемый для LLM вид
            output = []
            if response.get("answer"):
                output.append(f"Краткий ответ: {response['answer']}\n")
            output.append("Найденные результаты:")
            for idx, result in enumerate(response.get("results", []), 1):
                title = result.get("title", "Без заголовка")
                url = result.get("url")
                content = result.get("content", "")
                # Ограничим длину контента, чтобы не перегружать контекст
                if len(content) > 500:
                    content = content[:500] + "..."
                output.append(f"{idx}. {title}\n   URL: {url}\n   Содержание: {content}\n")
            return "\n".join(output)
        except Exception as e:
            return f"Ошибка поиска Tavily: {str(e)}"


class ResearcherAgent:
    """
    Субагент-исследователь, использующий GroqLLM и поисковый инструмент Tavily.
    """
    def __init__(self, llm: GroqLLM, search_tool: TavilySearchTool, max_iterations: int = 3):
        self.llm = llm
        self.search_tool = search_tool
        self.max_iterations = max_iterations
        self._iteration_count = 0
        self._last_calls = []  # для защиты от повторов (храним (tool_name, args))

        # Устанавливаем системный промпт для исследователя
        system_prompt = (
            "Ты — ИИ-исследователь. Твоя задача — собирать актуальную информацию из интернета.\n"
            "У тебя есть инструмент 'tavily_search'. Если тебе нужны свежие данные, вызови этот инструмент, передав поисковый запрос.\n"
            "Когда получишь результаты, проанализируй их и дай пользователю полный, структурированный ответ.\n"
            "Не выдумывай информацию, всегда опирайся на результаты поиска.\n"
            "Не вызывай один и тот же поисковый запрос повторно. Если информация не найдена, сообщи об этом."
        )
        self.llm.set_system_prompt(system_prompt)

        # Описание инструмента для GroqLLM (в формате, который понимает Groq/OpenAI)
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
        # Передаём инструменты в LLM (если ваш класс поддерживает их обновление)
        self.llm.tools = self.tools

    async def research(self, query: str) -> str:
        """Главный метод: принимает вопрос, возвращает готовый исследовательский ответ."""
        self._iteration_count = 0
        self._last_calls.clear()

        # Начинаем диалог с пользовательского запроса
        current_input = query

        while self._iteration_count < self.max_iterations:
            self._iteration_count += 1
            response = await self.llm.call(current_input)

            # Если LLM вернула список tool_calls
            if isinstance(response, list) and len(response) > 0 and "tool_calls" in response[0]:
                # На самом деле GroqLLM возвращает tool_calls в виде списка объектов, но упростим:
                # Предполагаем, что response — это список tool_calls (как в вашей реализации)
                # Приведём к общему виду
                tool_calls = response if isinstance(response, list) else response.get("tool_calls", [])
                if not tool_calls:
                    # Если нет вызовов, но пришёл список без tool_calls — это ошибка, выходим
                    return "Не удалось обработать запрос исследователя."
                # Выполняем все вызовы (обычно один)
                for tool_call in tool_calls:
                    func_name = tool_call.get("function", {}).get("name")
                    arguments = json.loads(tool_call.get("function", {}).get("arguments", "{}"))
                    # Защита от повторных вызовов с теми же аргументами
                    call_key = (func_name, frozenset(arguments.items()))
                    if call_key in self._last_calls:
                        # Повторный вызов – прерываем и возвращаем ошибку
                        return f"Обнаружен повторный вызов {func_name} с теми же аргументами. Исследование прервано."
                    self._last_calls.append(call_key)

                    if func_name == "tavily_search":
                        search_query = arguments.get("query")
                        if not search_query:
                            observation = "Ошибка: не указан поисковый запрос."
                        else:
                            observation = await self.search_tool.search(search_query)
                    else:
                        observation = f"Неизвестный инструмент: {func_name}"

                    # Отправляем результат обратно LLM (как сообщение от инструмента)
                    # Ваш класс GroqLLM не имеет прямого метода добавить tool_result, поэтому сделаем через историю вручную
                    # Но проще: добавим сообщение с ролью "tool" вручную в историю llm
                    self.llm.history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.get("id"),
                        "content": observation
                    })
                    # После добавления результата, продолжим цикл: теперь current_input = None, но LLM обработает результат
                    # и дальше либо вернёт финальный ответ, либо новые tool_calls.
                # После обработки всех вызовов, устанавливаем current_input в пустую строку, чтобы LLM продолжила с историей
                current_input = ""
                continue  # переходим к следующей итерации цикла, где вызовем llm.call с пустым вводом

            # Если response — это строка (текстовый ответ)
            elif isinstance(response, str):
                return response.strip()

            else:
                # Неожиданный формат ответа
                return f"Неожиданный ответ от LLM: {response}"

        # Если превышен лимит итераций
        return "Исследование достигло максимального числа шагов и не завершилось. Попробуйте упростить запрос."


# ------------------- Пример использования -------------------
async def main():
    # Инициализация GroqLLM (ваш класс)
    llm = GroqLLM(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        max_tokens=1024,
        tools=None  # будет установлено внутри ResearcherAgent
    )
    # Инициализация поискового инструмента
    tavily_api_key = "tvly-ваш_ключ"
    search_tool = TavilySearchTool(api_key=tavily_api_key)

    researcher = ResearcherAgent(llm, search_tool, max_iterations=3)

    query = "Каковы последние достижения в области квантовых вычислений за 2025-2026 годы?"
    result = await researcher.research(query)
    print("=== РЕЗУЛЬТАТ ИССЛЕДОВАНИЯ ===")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
