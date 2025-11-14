from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TOKEN
from chat_memory import ChatMemory
import ollama
import re

# Initialize chat memory
memory = ChatMemory(max_history=5)

# Ollama configuration
OLLAMA_MODEL = "gemma3:4b-it-qat"

# Helper functions
def is_story_request(message: str) -> bool:
    """Determine if the message is requesting a story/creative content."""
    message_lower = message.lower()
    story_keywords = [
        "казка", "казку", "уяви", "придумай", "історію", 
        "вигадати", "story", "fiction", "казкову", "історія"
    ]
    count = sum(1 for word in story_keywords if word in message_lower)
    return count > 0

# Select system prompt based on message type
def get_system_prompt(user_message: str) -> str:
    """Select appropriate system prompt based on message type."""
    if is_story_request(user_message):
        return (
            "Ти креативний асистент, який пише короткі вигадані історії та казки. "
            "Відповідай яскравою та образною мовою. "
            "Обмежуй відповідь до 300 символів. Зроби історію компактною, але цікавою. "
            "Уникай технічної мови або реальних фактів."
        )
    else:
        return (
            "Ти стислий та інформативний асистент. "
            "Відповідай на запитання корисно, прямо та зрозуміло. "
            "Обмеж відповідь одним коротким реченням, не довше 100 символів. "
            "Уникай зайвих деталей або повторень."
        )

# Async function to query Ollama model
async def ask_ollama(prompt: str, system_prompt: str, context_history: str = "") -> str:
    """
    Send request to Ollama and get response.
    
    Args:
        prompt: User's message
        system_prompt: System instructions for the model
        context_history: Previous conversation context
    
    Returns:
        Model's response text
    """
    try:
        # Build messages for Ollama chat API
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add context history if available
        if context_history:
            messages.append({"role": "assistant", "content": f"Попередній контекст: {context_history}"})
        
        # Add current user message
        messages.append({"role": "user", "content": prompt})
        
        # Call Ollama
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages
        )
        
        return response['message']['content']
    
    except Exception as e:
        print(f"Ollama error: {e}")
        return "Вибачте, виникла помилка при обробці запиту."

# Command handlers
async def process_ptic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main command handler for /ptic - processes user queries with AI."""
    user_message = ' '.join(context.args)

    if not user_message:
        await update.message.reply_text("Введіть запит після команди /ptic.")
        return

    # Get user ID for memory management
    user_id = update.message.from_user.id
    
    # Get conversation history
    context_history = memory.get_context(user_id)
    
    # Select appropriate system prompt
    system_prompt = get_system_prompt(user_message)
    
    # Get response from Ollama (no translation needed!)
    response = await ask_ollama(user_message, system_prompt, context_history)
    
    # Store in memory
    memory.add_message(user_id, user_message, response)
    
    # Send response
    await update.message.reply_text(response)

# Welcome message handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message when user starts the bot."""
    await update.message.reply_text("Привіт! Напиши /ptic і своє питання чи історію.")

# Command handler for creating polls
async def create_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create a Telegram poll from user input."""
    user_message = ' '.join(context.args)

    if not user_message:
        await update.message.reply_text(
            "Будь ласка, введіть запит для створення опитування. Приклад:\n"
            "/createpoll Якого кольору вода (чорна, зелена) anon multi"
        )
        return

    # Check for anonymous and multi-choice flags
    anonymous = 'anon' in user_message.lower()
    multi_choice = 'multi' in user_message.lower()

    # Clean service words
    cleaned_message = re.sub(r'\b(anon|multi)\b', '', user_message, flags=re.IGNORECASE).strip()

    # Extract question and options using regex
    match = re.search(r"(.*)\((.*)\)", cleaned_message)
    if match:
        question = match.group(1).strip()
        options_str = match.group(2).strip()
        options = [opt.strip() for opt in options_str.split(',') if opt.strip()]

        if len(options) < 2:
            await update.message.reply_text("Опитування повинно мати хоча б два варіанти.")
            return

        await update.message.reply_poll(
            question=question,
            options=options,
            is_anonymous=anonymous,
            allows_multiple_answers=multi_choice
        )
    else:
        await update.message.reply_text(
            "Не вдалося зрозуміти питання та варіанти для опитування. Спробуйте так:\n"
            "/createpoll Якого кольору вода (чорна, зелена) anon multi"
        )

def main():
    """Initialize and run the bot."""
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ptic", process_ptic))
    app.add_handler(CommandHandler("createpoll", create_poll))
    
    print(f"🤖 Бот запущено з моделлю {OLLAMA_MODEL}...")
    app.run_polling()

if __name__ == '__main__':
    main()