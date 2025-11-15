# PticAI - Telegram Bot with Ollama

Ukrainian language Telegram chatbot powered by Ollama and Gemma 3 4B model.

## Features

- 🇺🇦 Native Ukrainian language support
- 🤖 AI-powered responses using Gemma 3 4B (QAT)
- 💬 Conversation memory for context-aware responses
- 📖 Story generation mode for creative requests
- 📊 Poll creation functionality
- ⚡ Fast local inference via Ollama

## Requirements

- Python 3.8+
- Ollama installed and running
- Telegram Bot Token

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mklymchuk/PticAI.git
   cd PticAI
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Mac/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install python-telegram-bot ollama
   ```

4. **Install and setup Ollama:**
   ```bash
   # Install Ollama (if not already installed)
   # Visit: https://ollama.com

   # Pull the model
   ollama pull gemma3:4b-it-qat
   ```

5. **Configure bot token:**
   - Create `config.py` with your Telegram bot token:
   ```python
   TOKEN = "your_telegram_bot_token_here"
   ```

## Usage

### Run the Telegram Bot
```bash
python bot.py
```

### Test via CLI
```bash
python main.py
```

### Telegram Commands
- `/start` - Welcome message
- `/ptic <your message>` - Ask bot a question or request a story
- `/createpoll <question> (option1, option2) [anon] [multi]` - Create a poll

## Project Structure

```
PticAI/
├── bot.py              # Main Telegram bot
├── main.py             # CLI testing interface
├── chat_memory.py      # Conversation context management
├── config.py           # Configuration (bot token)
├── benchmark.py        # Performance testing
└── README.md           # This file
```

## Performance

- Average response time: ~2-4 seconds (depending on query complexity)
- Memory usage: ~2.6GB RAM (QAT quantization)
- Supports 128K token context window

## Development

This project was developed as part of the **AI Fluency: Framework & Foundations** course (Anthropic).

### Running Benchmarks
```bash
python benchmark.py
```

## AI Collaboration Acknowledgment

In creating this Telegram bot upgrade project from Llama 1B to Ollama with Gemma 3 4B, I collaborated with Claude (Anthropic) to assist with:

- **Project planning and delegation strategy**
- **Model research and selection guidance**
- **Code refactoring from local GGUF models to Ollama API**
- **Removing translation layer and implementing native Ukrainian support**
- **Performance benchmarking approach**
- **Git version control setup and best practices**

I affirm that all AI-generated and co-created content underwent thorough review and evaluation. I personally tested all code, made final decisions on architecture and model selection, and validated performance on my hardware. The final output accurately reflects my understanding, expertise, and intended meaning. While AI assistance was instrumental in the process, I maintain full responsibility for the content, its accuracy, and its presentation. This disclosure is made in the spirit of transparency and to acknowledge the role of AI in the creation process.

## License

This project is for educational purposes as part of the AI Fluency course.

## Author

Created by [Mykola Klymchuk](https://github.com/mklymchuk)

---

**Last Updated:** November 2025