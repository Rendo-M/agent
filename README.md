# Agent Project

This repository contains a small asynchronous Telegram bot and API backend with reminder functionality.

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Set `BOT_TOKEN` in `.env`
3. Start API: `uvicorn api.main:app --reload --host 127.0.0.1 --port 8000`
4. Start bot: `python bot/bot.py`

## Documentation

- [Architecture](docs/architecture.md) - System design and components
- [Setup Guide](docs/setup.md) - Detailed installation and configuration
- [Bot Commands](docs/bot.md) - Telegram bot usage
- [API Reference](docs/api.md) - REST API documentation
- [Database](docs/database.md) - SQLite schema and operations

### Документация на Русском

- [Архитектура](docs/ru/architecture.md) - Дизайн системы и компоненты
- [Руководство по Установке](docs/ru/setup.md) - Детальная установка и конфигурация
- [Команды Бота](docs/ru/bot.md) - Использование Telegram бота
- [API Ссылка](docs/ru/api.md) - Документация REST API
- [База Данных](docs/ru/database.md) - Схема SQLite и операции

## Structure

- `api/main.py` - FastAPI service
- `agent/` - AI agent logic (core.py, llm.py)
- `bot/` - Telegram bot package
  - `bot.py` - Main bot application
  - `client.py` - HTTP client wrapper
  - `help_generator.py` - Help text generator
- `services/` - Additional services package
  - `reminders.py` - Reminder engine
- `docs/` - Documentation (English + Russian)
- `requirements.txt` - Dependencies

## Features

- 🤖 AI-powered chat via Ollama/llama3.1
- 📅 Reminder system with SQLite storage
- 🔄 Asynchronous HTTP with session pooling
- ⚡ FastAPI backend
- 📱 Telegram bot integration

## Bot Commands

- `/start` - Initialize bot
- `/help` - Show help information
- `/add <name> <period> <time> <day>` - Add reminder
- `/reminders` - List reminders
- `/deactivate <name>` or `/del <name>` - Disable or delete reminder

Any other message is processed by the AI agent.
