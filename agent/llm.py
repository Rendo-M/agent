# # agent/llm.py
# import aiohttp

# OLLAMA_URL = "http://localhost:11434/api/chat"
# MODEL = "llama3.1:latest"


# async def call_llm(prompt: str) -> str:
#     """Send the prompt to Ollama and return the model's answer. / Отправляет промпт в Ollama и возвращает ответ модели."""
#     payload = {
#         "model": MODEL,
#         "messages": [
#             {"role": "user", "content": prompt}
#         ],
#         "stream": False,
#         "options": {
#             "temperature": 0.2,
#             "num_ctx": 4096,
#             "num_predict": 256
#         }
#     }

#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.post(OLLAMA_URL, json=payload, timeout=aiohttp.ClientTimeout(total=300)) as response:
#                 data = await response.json()
#                 return data["message"]["content"].strip()

#     except Exception as e:
#         return f"LLM error: {str(e)}"
# agent/llm.py
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

MODEL = "llama-3.1-8b-instant"


async def call_llm(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 256
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                GROQ_URL,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:

                data = await response.json()

                # 🔴 обработка ошибок Groq
                if "error" in data:
                    return f"Groq error: {data['error']}"

                # 🔴 защита от пустого ответа
                if "choices" not in data:
                    return f"Bad response: {data}"

                return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        
        return f"LLM error: {str(e)}"+(GROQ_API_KEY)