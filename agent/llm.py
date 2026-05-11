# agent/llm.py
import aiohttp

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.1:latest"


async def call_llm(prompt: str) -> str:
    """Send the prompt to Ollama and return the model's answer. / Отправляет промпт в Ollama и возвращает ответ модели."""
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_ctx": 4096,
            "num_predict": 256
        }
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(OLLAMA_URL, json=payload, timeout=aiohttp.ClientTimeout(total=300)) as response:
                data = await response.json()
                return data["message"]["content"].strip()

    except Exception as e:
        return f"LLM error: {str(e)}"