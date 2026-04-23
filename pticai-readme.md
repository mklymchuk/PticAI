# PticAI - Telegram Bot with Ollama (Gemma 4 Edition)

Ukrainian language Telegram chatbot powered by Ollama and the latest Gemma 4 E2B model. This project is optimized for local execution on hardware with limited VRAM (like Mac or edge devices) while maintaining high-quality conversational AI capabilities.

## 🌟 Features

- 🇺🇦 **Native Ukrainian Support** — No translation layers; the model reasons and responds natively in Ukrainian.
- 🧠 **Gemma 4 E2B (4-bit)** — Leveraging the latest Google's edge-optimized model for superior reasoning.
- 💬 **Smart Context Memory** — Maintains multi-turn conversations using a structured history system.
- 🎭 **Adaptive System Prompts** — Automatically switches between "Storyteller" and "General Assistant" modes based on user intent.
- 📊 **Poll Creation** — Build Telegram polls directly via bot commands using regex parsing.
- ⚡ **Performance Optimized** — Implements `keep-alive` to eliminate cold-start delays and regex-based "thinking" token filtering.

## 🛠 Requirements

- **Python 3.8+**
- **Ollama** (installed and running)
- **Telegram Bot Token** (from @BotFather)

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mklymchuk/PticAI.git
   cd PticAI
   ```

2. **Create and activate virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Mac/Linux
   # or .venv\Scripts\activate on Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install python-telegram-bot ollama psutil
   ```

4. **Setup Ollama & Model:**

   ```bash
   # Pull the latest Gemma 4 model optimized for edge devices
   ollama pull gemma4:e2b-it-q4_K_M
   ```

5. **Configure bot token:**

   Create a `config.py` file in the root directory:

   ```python
   TOKEN = "your_telegram_bot_token_here"
   ```

## 📋 Usage

### Run the Telegram Bot

```bash
python bot.py
```

### Test via CLI (Sandbox mode)

```bash
python main.py
```

### Telegram Commands

- `/start` — Initial greeting and command list  
- `/ptic <message>` — General chat, questions, or creative story requests  
- `/createpoll <question> (option1, option2) [anon] [multi]` — Create a poll  

## 📂 Project Structure

```text
PticAI/
├── bot.py              # Main Telegram bot logic
├── main.py             # CLI sandbox for local testing
├── chat_memory.py      # Persistence & context history management
├── config.py           # Sensitive configuration (excluded from Git)
├── benchmark.py        # Performance & hardware testing script
└── chat_logs.json      # Local storage for conversation history
```

## 📊 Performance (Tested on Mac)

Benchmark results for `gemma4:e2b-it-q4_K_M`:

- **Generation Speed:** ~20–22 tokens/sec (Near-instant response)  
- **Time to First Token (TTFT):** ~0.45s (with model warm-up)  
- **Memory Footprint:** ~1.8GB VRAM/RAM (4-bit K_M quantization)  

## 🔧 Technical Notes

- **Context Retention:** The bot uses a list-based message structure for history, which is more effective for Gemma 4 than raw text blocks  
- **Thinking Tags:** Gemma 4 uses internal "thinking" tokens (`<|think|>`). This project includes a cleaning layer to ensure users see only the final output  
- **Hardware Acceleration:** Fully compatible with Apple Silicon (Metal) and NVIDIA (CUDA) through Ollama's back-end  

## 👤 Author

Created by [Mykola Klymchuk](https://github.com/mklymchuk)

---

**Last Updated:** April 2026