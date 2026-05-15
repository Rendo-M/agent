import aiohttp
import os
from dotenv import load_dotenv


class GroqLLM:
    def __init__(
        self,
        model: str = "llama-3.1-8b-instant",
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 256,
        tools: list | None = None
    ):
        load_dotenv()

        self.api_key = os.getenv("GROQ_API_KEY")
        self.url = "https://api.groq.com/openai/v1/chat/completions"

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.tools = tools  # optional

        self.history = []

        if system_prompt:
            self.history.append({
                "role": "system",
                "content": system_prompt
            })

    # ---------------- CORE ----------------

    async def call(self, prompt: str) -> str:
        # 1. add user message
        self.history.append({
            "role": "user",
            "content": prompt
        })

        # 2. build payload
        payload = {
            "model": self.model,
            "messages": self.history,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        # 3. optional tools
        if self.tools:
            payload["tools"] = self.tools
            payload["tool_choice"] = "auto"

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

                    # error handling
                    if "error" in data:
                        return f"Groq error: {data['error']}"

                    if "choices" not in data:
                        return f"Bad response: {data}"

                    message = data["choices"][0]["message"]

                    # 4. tool calling case
                    if "tool_calls" in message:
                        self.history.append({
                            "role": "assistant",
                            "content": None,
                            "tool_calls": message["tool_calls"]
                        })

                        return message["tool_calls"]

                    # 5. normal text response
                    answer = message["content"].strip()

                    self.history.append({
                        "role": "assistant",
                        "content": answer
                    })

                    return answer

        except Exception as e:
            return f"LLM error: {str(e)}"

    # ---------------- UTIL ----------------

    def clear_history(self):
        self.history = []

    def set_system_prompt(self, prompt: str):
        self.history = [{
            "role": "system",
            "content": prompt
        }]