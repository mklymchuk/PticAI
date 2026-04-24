import ollama
import re
import base64
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from config import TOKEN
from database import BotDatabase

# Ініціалізація БД та моделі
db = BotDatabase()
OLLAMA_MODEL = "gemma4:e2b-it-q4_K_M"

# --- ЛОГІКА ПЕРСОНАЛІЗАЦІЇ (RAG) ---

def get_personalized_prompt(user_id, user_message):
    """Формує системний промпт на основі характеру та даних з БД."""
    message_lower = user_message.lower()
    
    # Визначаємо базовий характер
    if any(word in message_lower for word in ["казка", "історія", "придумай", "уяви"]):
        base_style = "Ти талановитий оповідач ПтіцШІ. Пиши цікаво, емоційно та лаконічно українською мовою."
    else:
        base_style = "Ти — ПтіцШІ, приязний, розумний та дотепний асистент. Спілкуйся українською, уникай офіціозу."

    # RAG: Підтягуємо знання про користувача
    profile = db.get_profile(user_id)
    if profile:
        bio, interests = profile
        personal_context = f"\nКонтекст про співрозмовника: {bio or 'немає даних'}. Інтереси: {interests or 'невідомі'}."
        personal_context += " Використовуй ці факти, щоб зробити розмову персональною, але не повторюй їх як робот."
        return base_style + personal_context
    
    return base_style

# --- ВЗАЄМОДІЯ З AI ---

async def ask_ollama(prompt: str, system_prompt: str, history: list, image_base64: str = None) -> str:
    try:
        messages = [{"role": "system", "content": system_prompt}]
        
        # Додаємо історію повідомлень з БД
        for msg in history:
            messages.append({"role": "user", "content": msg['user']})
            messages.append({"role": "assistant", "content": msg['bot']})
            
        user_content = {"role": "user", "content": prompt}
        if image_base64:
            user_content["images"] = [image_base64]
            
        messages.append(user_content)
        
        response = ollama.chat(model=OLLAMA_MODEL, messages=messages, keep_alive="30m")
        content = response['message']['content']
        
        # Очищення тегів міркування Gemma 4
        clean_content = re.sub(r'<\|think\|>.*?<\|channel\|>', '', content, flags=re.DOTALL).strip()
        # Прибираємо можливі залишки технічних тегів
        clean_content = re.sub(r'<[^>]+>', '', clean_content)
        
        return clean_content if clean_content else "Замислився і забув, що хотів сказати... Спробуй ще раз!"
    except Exception as e:
        return f"⚠️ Помилка ПтіцШІ: {e}"

# --- ФОНОВИЙ АНАЛІЗАТОР ---

async def analyze_user_identity(user_id, chat_history):
    """Аналізує останні репліки та оновлює профіль користувача в БД."""
    if len(chat_history) < 2: return

    formatted_history = "\n".join([f"User: {m['user']}\nBot: {m['bot']}" for m in chat_history])
    
    analysis_prompt = (
        "Проаналізуй діалог і витягни ТІЛЬКИ НОВІ важливі факти про користувача "
        "(ім'я, професія, хобі, техніка, вподобання). Якщо нового немає, напиши 'нічого'.\n\n"
        f"Діалог:\n{formatted_history}"
    )

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": "Ти аналітичний модуль. Твоя задача — стисло фіксувати факти про особу."},
                {"role": "user", "content": analysis_prompt}
            ]
        )
        new_facts = response['message']['content'].strip()
        
        if "нічого" not in new_facts.lower():
            current = db.get_profile(user_id)
            old_bio = current[0] if current else ""
            # Оновлюємо біо, додаючи нові факти
            updated_bio = f"{old_bio}\n{new_facts}".strip()
            db.update_profile(user_id, bio=updated_bio)
            print(f"📝 Профіль {user_id} автоматично оновлено.")
    except Exception as e:
        print(f"⚙️ Помилка аналізатора: {e}")

# --- ОБРОБНИКИ ТЕЛЕГРАМ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Я ПтіцШІ. 🐦\n"
        "Я не просто бот, я запам'ятовую наше спілкування, щоб ставати кращим для тебе.\n\n"
        "🔹 Пиши мені через /ptic або просто згадуй @нім_бота\n"
        "🔹 Надсилай фото — я їх бачу!\n"
        "🔹 Створюй опитування через /createpoll"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    
    # Визначаємо текст запиту (команда або згадка)
    if context.args:
        user_message = ' '.join(context.args)
    elif update.message.text:
        user_message = re.sub(r'@\w+', '', update.message.text).strip()
    else: return

    if not user_message: return

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    system_prompt = get_personalized_prompt(chat_id, user_message)
    history = db.get_recent_history(chat_id, limit=8)
    
    response = await ask_ollama(user_message, system_prompt, history)
    
    # Зберігаємо в БД
    db.add_to_history(chat_id, "user", user_message)
    db.add_to_history(chat_id, "assistant", response)
    
    await context.bot.send_message(chat_id=chat_id, text=response)
    
    # Запуск аналізатора кожні 5 повідомлень
    if db.get_history_count(chat_id) % 5 == 0:
        asyncio.create_task(analyze_user_identity(chat_id, db.get_recent_history(chat_id, limit=5)))

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    is_private = update.message.chat.type == 'private'
    has_mention = update.message.caption and f"@{context.bot.username}" in update.message.caption
    
    if not is_private and not has_mention: return

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        image_base64 = base64.b64encode(photo_bytes).decode('utf-8')
        
        user_caption = update.message.caption or "Що на цьому зображенні?"
        user_caption = re.sub(r'@\w+', '', user_caption).strip()
        
        system_prompt = get_personalized_prompt(chat_id, user_caption)
        history = db.get_recent_history(chat_id, limit=5)
        
        response = await ask_ollama(user_caption, system_prompt, history, image_base64)
        
        db.add_to_history(chat_id, "user", f"[Фото] {user_caption}")
        db.add_to_history(chat_id, "assistant", response)
        
        await context.bot.send_message(chat_id=chat_id, text=response)
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"⚠️ Не зміг обробити фото: {e}")

async def create_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = ' '.join(context.args)
    match = re.search(r"(.*)\((.*)\)", user_msg)
    if match:
        q = match.group(1).strip()
        opts = [o.strip() for o in match.group(2).split(',') if o.strip()]
        await update.message.reply_poll(question=q, options=opts)

# --- ЗАПУСК ---

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ptic", handle_message))
    app.add_handler(CommandHandler("createpoll", create_poll))
    
    app.add_handler(MessageHandler(filters.TEXT & filters.Entity("mention"), handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print(f"🤖 ПтіцШІ активовано. Модель: {OLLAMA_MODEL}")
    app.run_polling()

if __name__ == '__main__':
    main()