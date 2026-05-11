# agent/core.py
from agent.llm import call_llm

def build_prompt(text: str) -> str:
    """Build a prompt for the language model from user input. / Строит промпт для языковой модели из ввода пользователя."""
    return f"""
Ты AI-агент.

У тебя есть инструмент поиска напоминаний.

Если пользователь:
- спрашивает о напоминаниях
- спрашивает когда что-то сделать
- спрашивает про оплату, таблетки, дела, встречи
- хочет найти напоминание

ТОГДА отвечай СТРОГО в формате:

TOOL:search_reminders:<запрос>

Примеры:
User: когда платить интернет?
TOOL:search_reminders:интернет

User: когда таблетки?
TOOL:search_reminders:таблетки

Если инструмент не нужен — отвечай обычным текстом.

Никогда не объясняй свои действия.
Никогда не добавляй текст перед TOOL.

User: {text}
"""

async def run_agent(text: str, user_id: str = None, reminder_engine=None, max_tool_calls: int = 5) -> str:
    """Run the AI agent with the given text and return its response. / Запускает ИИ-агента для заданного текста и возвращает его ответ."""
    original_text = text
    call_count = 0
    prompt = build_prompt(original_text)
    while call_count < max_tool_calls:
        
        answer = await call_llm(prompt)
        call_count += 1
        
        # Check if the model requests a tool call
        if answer.startswith("TOOL:search_reminders:"):
            if not reminder_engine or not user_id:
                return "Ошибка: функция поиска недоступна"
            
            # Extract search query from the tool call
            search_query = answer.replace("TOOL:search_reminders:", "").strip()
            
            # Search reminders in the database
            reminders_found = reminder_engine.search_reminders(user_id, search_query)
            
            # Create a new prompt with search results for the model
            prompt = f"""Пользователь спросил: {original_text}

Найдены напоминания:
{reminders_found}

Сообщи о найденных напоминаниях пользователю кратко и удобно."""
            # Continue the loop to get the final answer
            continue
        else:
            # No tool call, return the answer
            return answer
    
    # If we've reached max tool calls, return the last answer
    return answer