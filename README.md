# PticAI - Telegram Bot with Ollama (Gemma 4 RAG Edition)

Ukrainian language Telegram chatbot powered by Ollama and the latest Gemma 4 E2B model. This project is a lightweight **RAG (Retrieval-Augmented Generation)** implementation designed for local execution on hardware with limited VRAM (like Mac or edge devices).

## 🌟 Особливості (Features)

* 🇺🇦 **Native Ukrainian Support** — Пряма робота з українською мовою без перекладачів
* 🧠 **Persistent User Memory (RAG)** — Автоматичний аналізатор витягує факти про користувача та зберігає їх у БД для персоналізації
* 🗄️ **SQLite Backend** — Надійне зберігання історії повідомлень та профілів (замість JSON)
* 👁️ **Vision Capabilities** — Аналіз та опис зображень прямо в Telegram
* 🤖 **Background Analysis** — Асинхронне оновлення профілю без блокування чату
* ⚡ **Performance Optimized** — `keep-alive`, фільтрація thinking-токенів, швидкий відгук

## 🛠 Вимоги (Requirements)

* **Python 3.10+**
* **Ollama**
* **Telegram Bot Token** (від @BotFather)

## 🚀 Встановлення (Installation)

### 1. Clone repository

```bash
git clone https://github.com/mklymchuk/PticAI.git
cd PticAI
```

### 2. Virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install python-telegram-bot ollama
```

### 4. Setup model

```bash
ollama pull gemma4:e2b-it-q4_K_M
```

### 5. Config

Створи `config.py`:

```python
TOKEN = "your_token_here"
```

## 📋 Використання (Usage)

### Run bot

```bash
python bot.py
```

### Telegram команди

* `/start` — старт
* `/ptic <text>` — чат з ботом
* `/saveme <info>` — зберегти факт про себе
* `/createpoll <question> (opt1, opt2)` — створити опитування

## 📂 Структура проекту

```text
PticAI/
├── bot.py
├── database.py
├── config.py
└── ptic_data.db
```

## ⚙️ Як працює RAG

1. **Retrieval** — дістає історію та профіль із SQLite
2. **Context Injection** — додає їх у system prompt
3. **Generation** — модель генерує відповідь
4. **Auto-Analysis** — фоново оновлює профіль

## 📊 Продуктивність

* ~20–22 tokens/sec
* ~0.4s TTFT
* ~1.8GB RAM

## ⚠️ Security

Файл `ptic_data.db` містить приватні дані.
Додай у `.gitignore`:

```
ptic_data.db
```

## 👤 Author

Mykola Klymchuk
https://github.com/mklymchuk

---

**Last Updated:** April 2026
