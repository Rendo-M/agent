# core/llm/llm.py

import os
import aiohttp

from dotenv import load_dotenv


class GroqLLM:
    """
    Stateless LLM client.
    Не хранит:
    - history
    - system prompt
    - state

    Только отправляет messages в Groq API.
    """

    def __init__(
        self,
        model: str = "llama-3.1-8b-instant",
        temperature: float = 0.2,
        max_tokens: int = 512
    ):
        load_dotenv()

        self.api_key = os.getenv("GROQ_API_KEY")
        self.url = "https://api.groq.com/openai/v1/chat/completions"

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def call(
        self,
        messages: list,
        tools: list | None = None,
        tool_choice: str = "auto"
    ) -> dict:
        """
        Возвращает:
        {
            "type": "text",
            "content": str
        }

        или

        {
            "type": "tool_calls",
            "content": list
        }
        """

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:

                    data = await response.json()

                    # ---------------- ERRORS ----------------

                    if "error" in data:
                        return {
                            "type": "error",
                            "content": data["error"]
                        }

                    if "choices" not in data:
                        return {
                            "type": "error",
                            "content": f"Bad response: {data}"
                        }

                    message = data["choices"][0]["message"]

                    # ---------------- TOOL CALLS ----------------

                    if "tool_calls" in message:
                        return {
                            "type": "tool_calls",
                            "content": message["tool_calls"]
                        }

                    # ---------------- TEXT ----------------

                    return {
                        "type": "text",
                        "content": message["content"].strip()
                    }

        except Exception as e:
            return {
                "type": "error",
                "content": str(e)
            }