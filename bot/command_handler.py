import asyncio
from datetime import datetime, timedelta
from typing import Optional

import aiohttp
from aiogram.types import Message

from bot.client import ApiClient, EmptyResponseError, ResponseValidationError
from bot.help_generator import HelpGenerator
from services.reminders import ReminderEngine
from services.logger import log_message


class BotCommandHandler:
    def __init__(self, api_client: ApiClient, reminder_engine: ReminderEngine):
        """Initialize the command handler with API and reminder services. / Инициализирует обработчик команд с API и сервисом напоминаний."""
        self.api_client = api_client
        self.reminder_engine = reminder_engine

    async def _send_message(self, message: Message, text: str) -> None:
        """Send a message and log it. / Отправляет сообщение и логирует его."""
        user_id = str(message.from_user.id)
        username = message.from_user.username or message.from_user.first_name or "Unknown"
        await message.answer(text)
        log_message(username, user_id, "snd", text)

    async def handle_message(self, message: Message) -> None:
        """Dispatch incoming messages to either command handling or AI requests. / Направляет входящее сообщение на обработку команды или запрос в ИИ."""
        text = (message.text or "").strip()
        if text.startswith("/"):
            await self.handle_command(message, text)
        else:
            await self.handle_api_request(message, text)

    async def handle_command(self, message: Message, text: str) -> None:
        """Parse a bot command and execute the corresponding action. / Разбирает команду бота и выполняет соответствующее действие."""
        parts = text.split(maxsplit=1)
        command = parts[0][1:].split("@", 1)[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if command == "start":
            await self.start(message)
        elif command == "add":
            await self.add_reminder(message, args)
        elif command == "reminders":
            await self.list_reminders(message)
        elif command == "set":
            await self.set_reminder(message, args)
        elif command == "deactivate":
            await self.deactivate_reminder(message, args)
        elif command in {"del", "delete"}:
            await self.delete_reminder(message, args)
        elif command == "help":
            await self.show_help(message, args)
        else:
            await message.answer("Неизвестная команда. Используйте /help для списка команд.")

    async def handle_api_request(self, message: Message, text: str) -> None:
        """Send non-command text to the AI backend and return its answer. / Отправляет текст без команды в backend ИИ и возвращает ответ."""
        user_id = str(message.from_user.id)
        try:
            answer = await self.api_client.request(user_id=user_id, text=text)
        except aiohttp.ClientResponseError as exc:
            await message.answer(f"API error {exc.status}: {exc.message}")
            return
        except asyncio.TimeoutError:
            await message.answer("Request timed out after 200 seconds.")
            return
        except EmptyResponseError:
            await message.answer("пустой ответ")
            return
        except ResponseValidationError:
            await message.answer("ошибка в ответе")
            return
        except Exception as exc:
            await message.answer(f"Unexpected error: {exc}")
            return

        await message.answer(answer)

    async def start(self, message: Message) -> None:
        """Respond to /start with a simple startup confirmation. / Отвечает на /start простым подтверждением запуска."""
        await message.answer("Бот запущен")

    async def add_reminder(self, message: Message, args: str) -> None:
        """Parse /add arguments and save a new reminder. / Разбирает аргументы /add и сохраняет новое напоминание."""
        user_id = str(message.from_user.id)
        parts = args.split()
        if len(parts) < 3:
            await message.answer("Использование: /add <name> <period> <time> <day> [comment]")
            return

        name = parts[0]
        period = parts[1].lower()
        reminder_time = parts[2]
        day: Optional[str] = None
        comment: Optional[str] = None

        if period not in ["daily", "weekly", "monthly", "yearly"]:
            await message.answer("Период должен быть: daily, weekly, monthly, yearly")
            return

        if period == "daily":
            if len(parts) > 3:
                comment = " ".join(parts[3:]).strip()
        else:
            if len(parts) < 4:
                await message.answer("Использование: /add <name> <period> <time> <day> [comment]")
                return
            day = parts[3]
            if len(parts) > 4:
                comment = " ".join(parts[4:]).strip()

        try:
            datetime.strptime(reminder_time, "%H:%M")
        except ValueError:
            await message.answer("Время должно быть в формате HH:MM")
            return

        if period == "weekly":
            if not day or not day.isdigit() or not (1 <= int(day) <= 7):
                await message.answer("Для weekly день должен быть числом от 1 до 7 (1=Пн, 7=Вс)")
                return
        elif period == "monthly":
            if not day or not day.isdigit() or not (1 <= int(day) <= 31):
                await message.answer("Для monthly день должен быть числом от 1 до 31")
                return
        elif period == "yearly":
            try:
                if not day:
                    raise ValueError()
                datetime.strptime(day, "%d.%m")
            except ValueError:
                await message.answer("Для yearly день должен быть в формате DD.MM")
                return

        if self.reminder_engine.add_reminder(user_id, name, period, reminder_time, day, comment):
            await message.answer(f"Напоминание '{name}' добавлено")
            await self.reminder_engine.refresh()
        else:
            await message.answer("Ошибка при добавлении напоминания")

    async def list_reminders(self, message: Message) -> None:
        """List all reminders for the current user. / Показывает все напоминания текущего пользователя."""
        user_id = str(message.from_user.id)
        reminders = self.reminder_engine.get_reminders(user_id)
        if not reminders:
            await message.answer("У вас нет напоминаний")
            return

        text = "Ваши напоминания:\n"
        for name, comment, period, rtime, day, due_at, active in reminders:
            status = "активно" if active else "неактивно"
            if period == "once":
                due_display = due_at.replace("T", " ") if due_at else f"{day} {rtime}"
                text += f"- {name} ({period}, {due_display}) - {status}\n"
            else:
                day_str = f", день: {day}" if day else ""
                comment_str = f": {comment}" if comment else ""
                text += f"- {name}{comment_str} ({period}, {rtime}{day_str}) - {status}\n"
        await message.answer(text)

    async def deactivate_reminder(self, message: Message, args: str) -> None:
        """Handle /deactivate and mark the reminder as inactive. / Обрабатывает /deactivate и помечает напоминание как неактивное."""
        user_id = str(message.from_user.id)
        name = args.strip().split()[0] if args.strip() else None
        if not name:
            await message.answer("Использование: /deactivate <name>")
            return

        if self.reminder_engine.deactivate_reminder(user_id, name):
            await message.answer(f"Напоминание '{name}' деактивировано")
        else:
            await message.answer(f"Напоминание '{name}' не найдено")

    async def delete_reminder(self, message: Message, args: str) -> None:
        """Handle /del and delete the named reminder. / Обрабатывает /del и удаляет указанное напоминание."""
        user_id = str(message.from_user.id)
        name = args.strip().split()[0] if args.strip() else None
        if not name:
            await message.answer("Использование: /del <name>")
            return

        if self.reminder_engine.delete_reminder(user_id, name):
            await message.answer(f"Напоминание '{name}' удалено")
        else:
            await message.answer(f"Напоминание '{name}' не найдено")

    async def set_reminder(self, message: Message, args: str) -> None:
        """Parse /set and create a one-time reminder after the relative time interval. / Разбирает /set и создает разовое напоминание через указанный интервал."""
        user_id = str(message.from_user.id)
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Использование: /set <hours:minutes> <comment>")
            return

        time_spec = parts[0]
        comment = parts[1].strip()
        if not comment:
            await message.answer("Использование: /set <hours:minutes> <comment>")
            return

        try:
            hours_str, minutes_str = time_spec.split(":", 1)
            hours = int(hours_str)
            minutes = int(minutes_str)
        except ValueError:
            await message.answer("Время должно быть в формате H:M или HH:MM")
            return

        if hours < 0 or minutes < 0 or minutes >= 60:
            await message.answer("Время должно быть положительным и минуты в диапазоне 0-59")
            return

        total_minutes = hours * 60 + minutes
        if total_minutes <= 0:
            await message.answer("Интервал должен быть больше нуля")
            return

        due = datetime.now() + timedelta(minutes=total_minutes)
        due_at = due.isoformat(timespec="minutes")
        reminder_time = due.strftime("%H:%M")
        day = due.strftime("%d.%m")
        name = comment

        if self.reminder_engine.add_reminder(user_id, name, "once", reminder_time, day, None, due_at):
            await message.answer(f"Разовое напоминание '{comment}' установлено на {due.strftime('%d.%m %H:%M')}")
        else:
            await message.answer("Ошибка при добавлении напоминания")

    async def show_help(self, message: Message, args: str) -> None:
        """Send help text for a specific command or general usage. / Отправляет справку для конкретной команды или общую справку."""
        if args:
            help_text = HelpGenerator.get_command_help(args.strip())
        else:
            help_text = HelpGenerator.get_help_text()

        await message.answer(help_text, parse_mode="Markdown")
