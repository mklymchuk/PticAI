import ollama
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TOKEN
from chat_memory import ChatMemory

# Initialize chat memory
memory = ChatMemory(max_history=8) # Збільшив історію, бо Gemma 4 добре її тримає
OLLAMA_MODEL = "gemma4:e2b-it-q4_K_M"

# --- Допоміжні функції ---

def get_system_prompt(user_message: str) -> str:
    """Визначає характер бота залежно від типу питання."""
    message_lower = user_message.lower()
    
    # Творчий режим
    if any(word in message_lower for word in ["казка", "історія", "придумай", "уяви"]):
        return (
            "Ти талановитий оповідач. Пиши цікаво, емоційно та лаконічно українською мовою. "
            "Твої історії мають бути компактними, але захопливими."
        )
    
    # Режим загального спілкування
    return (
        "Ти — Птіц, приязний та розумний асистент для спілкування. "
        "Відповідай українською мовою, будь дотепним, але лаконічним. "
        "Уникай довгих лекцій, спілкуйся як жива людина."
    )

async def ask_ollama(prompt: str, system_prompt: str, history: list) -> str:
    """Запит до моделі з урахуванням історії та очищенням виводу."""
    try:
        messages = [{"role": "system", "content": system_prompt}]
        
        # Додаємо історію повідомлень (якщо вона є)
        for msg in history:
            messages.append({"role": "user", "content": msg['user']})
            messages.append({"role": "assistant", "content": msg['bot']})
            
        messages.append({"role": "user", "content": prompt})
        
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            options={
                "temperature": 0.8, # Трохи більше творчості для спілкування
                "top_p": 0.9,
            },
            keep_alive="30m" # Тримаємо модель в пам'яті
        )
        
        content = response['message']['content']
        
        # Видаляємо теги думок Gemma 4, щоб вони не потрапили в чат
        clean_content = re.sub(r'<\|think\|>.*?<\|channel\|>', '', content, flags=re.DOTALL).strip()
        # Також прибираємо можливі технічні артефакти
        clean_content = re.sub(r'<[^>]+>', '', clean_content)
        
        return clean_content if clean_content else "Цікаве питання! Навіть не знаю, що відповісти."

    except Exception as e:
        print(f"Ollama error: {e}")
        return "Вибач, щось мозок підклинило. Спробуй ще раз!"

# --- Обробники команд ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вітальне повідомлення."""
    welcome_text = (
        "Привіт! Я Птіц — твій кишеньковий ШІ. 🐦\n\n"
        "Що я вмію:\n"
        "🔹 /ptic [питання] — поспілкуватися зі мною\n"
        "🔹 /createpoll Питання (Опція1, Опція2) — створити опитування\n\n"
        "Про що поговоримо сьогодні?"
    )
    await update.message.reply_text(welcome_text)

async def process_ptic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Основна логіка чату."""
    user_message = ' '.join(context.args)

    if not user_message:
        await update.message.reply_text("Напиши щось після /ptic, щоб я міг відповісти!")
        return

    user_id = update.message.from_user.id
    history = memory.get_messages(user_id) # Отримуємо список попередніх повідомлень
    system_prompt = get_system_prompt(user_message)
    
    # Показуємо статус друку
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    response = await ask_ollama(user_message, system_prompt, history)
    
    # Зберігаємо в пам'ять
    memory.add_message(user_id, user_message, response)
    
    await update.message.reply_text(response)

async def create_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Створення опитувань (повернуто на місце)."""
    user_message = ' '.join(context.args)

    if not user_message:
        await update.message.reply_text(
            "Приклад: /createpoll Який колір кращий? (Синій, Зелений) anon"
        )
        return

    anonymous = 'anon' in user_message.lower()
    multi_choice = 'multi' in user_message.lower()
    cleaned_message = re.sub(r'\b(anon|multi)\b', '', user_message, flags=re.IGNORECASE).strip()

    match = re.search(r"(.*)\((.*)\)", cleaned_message)
    if match:
        question = match.group(1).strip()
        options = [opt.strip() for opt in match.group(2).split(',') if opt.strip()]

        if len(options) < 2:
            await update.message.reply_text("Треба хоча б два варіанти у дужках!")
            return

        await update.message.reply_poll(
            question=question,
            options=options,
            is_anonymous=anonymous,
            allows_multiple_answers=multi_choice
        )
    else:
        await update.message.reply_text("Не зрозумів формат. Спробуй: Питання (Варіант1, Варіант2)")

# --- Запуск бота ---

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ptic", process_ptic))
    app.add_handler(CommandHandler("createpoll", create_poll))
    
    print(f"🤖 Птіц запущений з моделлю {OLLAMA_MODEL}")
    app.run_polling()

if __name__ == '__main__':
    main()