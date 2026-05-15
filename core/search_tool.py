# search_tool.py
from tavily import AsyncTavilyClient

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
                search_depth="basic",
                max_results=max_results,
                include_answer=True,
                include_raw_content=False
            )
            output = []
            if response.get("answer"):
                output.append(f"Краткий ответ: {response['answer']}\n")
            output.append("Найденные результаты:")
            for idx, result in enumerate(response.get("results", []), 1):
                title = result.get("title", "Без заголовка")
                url = result.get("url")
                content = result.get("content", "")
                if len(content) > 500:
                    content = content[:500] + "..."
                output.append(f"{idx}. {title}\n   URL: {url}\n   Содержание: {content}\n")
            return "\n".join(output)
        except Exception as e:
            return f"Ошибка поиска Tavily: {str(e)}"
