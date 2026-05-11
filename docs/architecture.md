# Architecture

## Overview

The Agent project is a Telegram bot with an AI-powered backend that provides conversational responses and reminder functionality. The system is built with asynchronous Python using FastAPI, aiogram, and aiohttp.

## Components

### 1. Telegram Bot (`bot/`)

- **bot.py**: Main bot application using aiogram
  - Handles user messages and commands
  - Manages per-user HTTP session pool (max 50 sessions)
  - Integrates reminder functionality
  - Runs background reminder worker

- **client.py**: HTTP client wrapper
  - Manages aiohttp sessions per user
  - Handles API requests with timeout (200s)
  - Validates responses and handles errors
  - Provides clean error messages in Russian

- **help_generator.py**: Help text generator
  - Generates formatted help messages for bot commands
  - Supports general help and command-specific help
  - Provides troubleshooting information

### 2. API Backend (`api/`)

- **main.py**: FastAPI application
  - Single endpoint `/run` for agent requests
  - Accepts JSON with `user_id` and `text`
  - Returns JSON with `answer` field
  - Fully asynchronous

### 3. Agent Core (`agent/`)

- **core.py**: Agent logic
  - Builds prompts from user input
  - Calls LLM asynchronously
  - Simple prompt template

- **llm.py**: LLM client
  - Uses aiohttp to call Ollama API
  - Configurable model (llama3.1:latest)
  - Handles timeouts and errors
  - Returns clean text responses

### 3. Services (`services/`)

- **reminders.py**: Reminder engine
  - SQLite database for persistent storage
  - Background worker checking reminders every minute
  - Supports daily/weekly/monthly/yearly periods
  - Sends reminders via bot to users

## Data Flow

1. **User Message** → Telegram Bot
2. **Bot** → HTTP Client → API Backend
3. **API** → Agent Core → LLM Client → Ollama
4. **Response** ← ← ← ← ← ← ← ← ← ←
5. **Bot** → User

## Asynchronous Design

- All network calls use aiohttp
- Bot uses aiogram's async framework
- Background tasks for reminders
- Session pooling for efficiency

## Database

- SQLite file: `reminders.db`
- Table: `reminders`
  - id, user_id, name, period, reminder_time, day, active

## Configuration

- Environment variables via `.env`
- BOT_TOKEN: Telegram bot token
- Ollama URL hardcoded (localhost:11434)

## Error Handling

- API errors: HTTP status + message
- Timeouts: 200s for API, 300s for LLM
- Validation: Response format checking
- User-friendly Russian error messages