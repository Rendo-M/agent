# Setup Guide

## Prerequisites

- Python 3.8+
- Telegram Bot Token (from @BotFather)
- Ollama running locally with llama3.1 model

## Installation

### 1. Clone/Download Project

```bash
cd /path/to/projects
# Assuming project is in d:\projects\agent
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Unix:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create `.env` file in project root:

```env
BOT_TOKEN=your_telegram_bot_token_here
```

Get bot token from Telegram's @BotFather.

### 5. Configuration Options

#### LLM Settings (in `agent/llm.py`)
- **OLLAMA_URL**: `"http://localhost:11434/api/chat"` (Ollama API endpoint)
- **MODEL**: `"llama3.1:latest"` (Ollama model name)
- **Timeout**: 300 seconds for LLM requests

#### Bot Settings (in `bot/client.py`)
- **API_URL**: `"http://127.0.0.1:8000/run"` (Backend API endpoint)
- **MAX_USER_SESSIONS**: 50 (Max HTTP sessions per user)
- **SESSION_TIMEOUT_SECONDS**: 200 (HTTP request timeout)

#### Reminder Settings (in `services/reminders.py`)
- **Database**: `reminders.db` (SQLite file)
- **Check Interval**: 60 seconds (How often to check for due reminders)

### 6. Setup Ollama

Ensure Ollama is running locally:

```bash
# Install Ollama if needed
# Pull the model
ollama pull llama3.1:latest
# Start Ollama service
ollama serve
```

## Running the Application

### Option 1: Manual Start

1. **Start API Backend**:
```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

2. **Start Bot** (in new terminal):
```bash
python bot/bot.py
```

### Option 2: Using Scripts

Create start scripts:

**start_api.bat** (Windows):
```batch
@echo off
call .venv\Scripts\activate
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

**start_bot.bat** (Windows):
```batch
@echo off
call .venv\Scripts\activate
python bot/bot.py
```

**start.sh** (Unix):
```bash
#!/bin/bash
source .venv/bin/activate
# Start API in background
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000 &
# Start bot
python bot/bot.py
```

## Testing

### Test API

```bash
curl -X POST "http://127.0.0.1:8000/run" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test", "text": "Hello"}'
```

### Test Bot

1. Find your bot on Telegram
2. Send `/start`
3. Send a message
4. Test reminder commands:
   - `/add test daily 10:00`
   - `/reminders`
   - `/deactivate test`

## Troubleshooting

### Common Issues

1. **Bot not responding**:
   - Check BOT_TOKEN in .env
   - Verify bot token with @BotFather
   - Check console for errors

2. **API connection failed**:
   - Ensure API is running on port 8000
   - Check firewall settings
   - Verify host IP (127.0.0.1)

3. **LLM errors**:
   - Ensure Ollama is running
   - Check model name in llm.py
   - Verify Ollama API on localhost:11434

4. **Import errors**:
   - Activate virtual environment
   - Reinstall requirements: `pip install -r requirements.txt`

### Logs

- Bot logs to console
- API logs via uvicorn
- Reminder engine logs via logging module

### Ports

- API: 8000
- Ollama: 11434
- Telegram: Dynamic

## Development

### Project Structure

```
agent/          # AI agent logic
api/            # FastAPI backend
bot/            # Telegram bot
services/       # Additional services (reminders)
docs/           # Documentation
```

### Adding Features

- Bot commands: Add to `bot/bot.py`
- API endpoints: Add to `api/main.py`
- Agent logic: Modify `agent/core.py`
- Database: Update `services/reminders.py`