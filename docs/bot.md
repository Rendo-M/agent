# Bot Documentation

## Overview

Telegram bot with AI agent integration and reminder functionality.

## Commands

### /start
Initializes the bot and shows welcome message.

**Usage**: `/start`

**Response**: "Бот запущен"

### /help
Shows help information about all commands.

**Usage**: `/help` or `/help <command>`

**Response**: Complete help text or help for specific command.

**Examples**:
- `/help` - Show all commands
- `/help add` - Show help for add command
- `/help reminders` - Show help for reminders command

### /add
Adds a new reminder.

**Usage**: `/add <name> <period> <time> <day>`

**Parameters**:
- `name`: Reminder name (string)
- `period`: One of: daily, weekly, monthly, yearly
- `time`: Time in HH:MM format (e.g., "14:30")
- `day`: Depends on period:
  - daily: omit or empty
  - weekly: 1-7 (1=Monday, 7=Sunday)
  - monthly: 1-31 (day of month)
  - yearly: DD.MM (e.g., "25.12" for Christmas)

**Examples**:
```
/add workout daily 08:00
/add meeting weekly 10:00 1
/add bill monthly 01:00 15
/add birthday yearly 09:00 25.12
```

**Validation**:
- Time must be valid HH:MM
- Day format depends on period
- Period must be one of the allowed values

### /reminders
Lists all user reminders.

**Usage**: `/reminders`

**Response**: List of reminders with status:
```
Ваши напоминания:
- workout (daily, 08:00) - активно
- meeting (weekly, 10:00, день: 1) - активно
```

### /deactivate
Deactivates a reminder by name.

**Usage**: `/deactivate <name>`

**Response**: Confirmation or "not found" message.

### /del
Deletes a reminder by name.

**Usage**: `/del <name>`

**Response**: Confirmation or "not found" message.

## Message Handling

Any non-command message is sent to the AI agent.

**Processing**:
1. Creates/reuses HTTP session for user
2. Sends request to API backend
3. Validates response
4. Returns answer or error message

**Error Messages** (in Russian):
- "ошибка в ответе" - Invalid response format
- "пустой ответ" - Empty answer
- "API error {status}: {message}" - HTTP errors
- "Request timed out after 200 seconds." - Timeout
- "Unexpected error: {exc}" - Other exceptions

## Background Features

### Session Management
- Maintains up to 50 HTTP sessions per user
- Sessions are reused across messages
- Oldest session evicted when limit reached
- Sessions closed on bot shutdown

### Reminder Worker
- Runs every minute in background
- Checks SQLite database for due reminders
- Sends reminder messages to users
- Supports all period types with proper date/time matching

## Technical Details

- Built with aiogram (async Telegram framework)
- Uses aiohttp for API calls with 200s timeout
- SQLite database for reminders
- Environment variable: `BOT_TOKEN`