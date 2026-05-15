# Telegram AI Agent Bot

A comprehensive Telegram bot with AI agent integration and reminder management system.

## Features

- **AI Agent Integration**: Powered by Ollama LLM for intelligent conversations
- **Reminder Management**: Full CRUD operations for reminders with natural language processing
- **Multi-modal Processing**: Handles text, voice, and image inputs
- **Modular Architecture**: Separate processors for different content types
- **Comprehensive Logging**: Detailed logging for all operations
- **Bilingual Support**: English and Russian documentation

## Project Structure

```
├── agent/              # AI agent core and tools
│   ├── core.py        # Main agent orchestration
│   ├── llm.py         # LLM integration
│   └── tools/         # AI tools for reminder operations
├── api/               # FastAPI backend server
│   └── main.py       # API endpoints
├── bot/               # Telegram bot components
│   ├── bot.py         # Main bot entry point
│   ├── command_handler.py  # Bot commands
│   ├── text_processor.py   # Text message processing
│   ├── audio_processor.py  # Voice message processing
│   └── image_processor.py  # Image processing
├── services/          # Core services
│   ├── reminders.py   # Reminder database operations
│   └── logger.py      # Logging configuration
└── requirements.txt   # Python dependencies
```

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   Create a `.env` file with:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2:3b
   ```

3. **Start Ollama Service**:
   Ensure Ollama is running with the specified model.

## Running the Application

### Option 1: Run Both Services (Recommended)

Use the launcher script to start both services:

```bash
python start.py
```

### Option 2: Run Services Separately

Start the API server and bot separately:

**Terminal 1 - API Server:**
```bash
python api/main.py
```

**Terminal 2 - Telegram Bot:**
```bash
python bot/bot.py
```

### Option 3: Using Uvicorn (API Server)

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8001
```

## Bot Commands

- `/start` - Initialize the bot
- `/help` - Show help information
- `/add <reminder>` - Add a new reminder
- `/reminders` - List all active reminders
- `/set <id> <new_text>` - Update reminder text
- `/del <id>` - Delete a reminder
- `/deactivate <id>` - Deactivate a reminder

## AI Agent Features

The bot includes an intelligent AI agent that can:
- Understand natural language requests for reminder operations
- Perform database operations through tool-based interactions
- Provide contextual responses
- Handle complex queries and multi-step operations

## API Endpoints

- `POST /run` - Process user input through the AI agent
  - Body: `{"user_id": "string", "text": "string"}`
  - Response: `{"answer": "string"}`

## Logging

All operations are logged to:
- Message logs: `logs/messages.log`
- Database operations: `logs/database.log`

## Development

The project uses a modular architecture with separate processors for different media types. Each component can be developed and tested independently.

### Adding New Processors

1. Create a new processor class inheriting from base processor
2. Implement the `process` method
3. Register the processor in `bot/bot.py`

### Extending AI Tools

Add new tools in `agent/tools/` following the existing pattern for tool-based LLM interactions.

- `/start` - Initialize bot
- `/help` - Show help information
- `/add <reminder>` - Add a new reminder
- `/reminders` - List all active reminders
- `/set <id> <new_text>` - Update reminder text
- `/del <id>` - Delete a reminder
- `/deactivate <id>` - Deactivate a reminder

Any other message is processed by the AI agent.
