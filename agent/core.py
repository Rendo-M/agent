# agent/core.py
from agent.llm import call_llm

def build_prompt(text):
    """Build a prompt for the language model from user input. / Строит промпт для языковой модели из ввода пользователя."""
    return f"""
User: {text}
Answer briefly and clearly.
"""

async def run_agent(text: str, user_id: str = None) -> str:
    """Run the AI agent with the given text and return its response. / Запускает ИИ-агента для заданного текста и возвращает его ответ."""
    prompt = build_prompt(text)
    answer = await call_llm(prompt)

    return answer