# Руководство по Установке

## Предварительные Требования

- Python 3.8+
- Токен Telegram Бота (от @BotFather)
- Ollama запущенный локально с моделью llama3.1

## Установка

### 1. Клонировать/Скачать Проект

```bash
cd /path/to/projects
# Предполагая что проект в d:\projects\agent
```

### 2. Создать Виртуальное Окружение

```bash
python -m venv .venv
# На Windows:
.venv\Scripts\activate
# На Unix:
source .venv/bin/activate
```

### 3. Установить Зависимости

```bash
pip install -r requirements.txt
```

### 4. Настроить Окружение

Создать файл `.env` в корне проекта:

```env
BOT_TOKEN=ваш_токен_telegram_бота_здесь
```

Получить токен бота от Telegram @BotFather.

### 5. Опции Конфигурации

#### Настройки LLM (в `agent/llm.py`)
- **OLLAMA_URL**: `"http://localhost:11434/api/chat"` (эндпоинт API Ollama)
- **MODEL**: `"llama3.1:latest"` (имя модели Ollama)
- **Таймаут**: 300 секунд для запросов LLM

#### Настройки Бота (в `bot/client.py`)
- **API_URL**: `"http://127.0.0.1:8000/run"` (эндпоинт backend API)
- **MAX_USER_SESSIONS**: 50 (макс. HTTP сессий на пользователя)
- **SESSION_TIMEOUT_SECONDS**: 200 (таймаут HTTP запросов)

#### Настройки Напоминаний (в `services/reminders.py`)
- **База данных**: `reminders.db` (файл SQLite)
- **Интервал проверки**: 60 секунд (как часто проверять напоминания)

### 6. Настройка Ollama

Убедиться что Ollama запущен локально:

```bash
# Установить Ollama если нужно
# Скачать модель
ollama pull llama3.1:latest
# Запустить сервис Ollama
ollama serve
```

## Запуск Приложения

### Вариант 1: Ручной Запуск

1. **Запустить API Backend**:
```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

2. **Запустить Бота** (в новом терминале):
```bash
python bot/bot.py
```

### Вариант 2: Используя Скрипты

Создать скрипты запуска:

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
# Запустить API в фоне
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000 &
# Запустить бота
python bot/bot.py
```

## Тестирование

### Тестировать API

```bash
curl -X POST "http://127.0.0.1:8000/run" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test", "text": "Привет"}'
```

### Тестировать Бота

1. Найти бота в Telegram
2. Отправить `/start`
3. Отправить сообщение
4. Протестировать команды напоминаний:
   - `/add тест ежедневно 10:00`
   - `/reminders`
   - `/deactivate тест`

## Устранение Неполадок

### Распространенные Проблемы

1. **Бот не отвечает**:
   - Проверить BOT_TOKEN в .env
   - Проверить токен бота с @BotFather
   - Проверить консоль на ошибки

2. **Ошибка подключения к API**:
   - Убедиться что API запущен на порту 8000
   - Проверить настройки firewall
   - Проверить IP хоста (127.0.0.1)

3. **Ошибки LLM**:
   - Убедиться что Ollama запущен
   - Проверить имя модели в llm.py
   - Проверить API Ollama на localhost:11434

4. **Ошибки импорта**:
   - Активировать виртуальное окружение
   - Переустановить requirements: `pip install -r requirements.txt`

### Логи

- Бот логирует в консоль
- API логирует через uvicorn
- Движок напоминаний логирует через модуль logging

### Порты

- API: 8000
- Ollama: 11434
- Telegram: Динамический

## Разработка

### Структура Проекта

```
agent/          # Логика ИИ-агента
api/            # FastAPI backend
bot/            # Telegram бот
services/       # Дополнительные сервисы (напоминания)
docs/           # Документация
```

### Добавление Функций

- Команды бота: Добавить в `bot/bot.py`
- API эндпоинты: Добавить в `api/main.py`
- Логика агента: Изменить `agent/core.py`
- База данных: Обновить `services/reminders.py`