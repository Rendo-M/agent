from fastapi import FastAPI
from pydantic import BaseModel

from agent.core import run_agent
from services.reminders import ReminderEngine

app = FastAPI()
reminder_engine = ReminderEngine()

class RequestData(BaseModel):
    user_id: str
    text: str

@app.post("/run")
async def run(data: RequestData):
    """Process user input through the AI agent and return the result. / Обрабатывает ввод пользователя через ИИ-агента и возвращает результат."""
    result = await run_agent(
        user_id=data.user_id,
        text=data.text,
        reminder_engine=reminder_engine
    )

    return {
        "answer": result
    }