from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TOKEN
from translator import TranslatorWrapper
from local_llm import LocalLLM
from chat_memory import ChatMemory
import re

translator = TranslatorWrapper()
model_path = "/Users/kola/.llama/hf_model_1B/hf_model_1B-1.2B-q8_0.gguf"

# Єдина модель
local_model = LocalLLM(model_path=model_path)

memory = ChatMemory(max_history=5)

# 🎨 Фільтр, що визначає, чи це історія
def is_story_request(message: str) -> bool:
    message_lower = message.lower()
    story_keywords = ["казка", "казку", "уяви", "придумай", "історію", "вигадати", "story", "fiction", "казкову", "історія"]

    count = sum(1 for word in story_keywords if word in message_lower)
    return count > 0

# 🧠 Команда /ptic — інтелектуальна обробка
async def process_ptic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = ' '.join(context.args)

    if not user_message:
        await update.message.reply_text("Введіть запит після команди /ptic.")
        return

    # Переклад користувацького запиту на англійську
    translated_input = translator.to_en(user_message)

    # Обираємо інструкцію (system prompt)
    if is_story_request(user_message):
        system_prompt = (
        "You are a creative assistant who writes short fictional or fairy-tale-like stories. "
        "Respond with vivid and imaginative language. "
        "Stay within 300 characters. Keep the story compact but engaging, and use a clear structure. "
        "Avoid technical language or real-world facts."
        )

    else:
        system_prompt = (
        "You are a concise and informative assistant. "
        "Answer user questions in a helpful, direct, and clear manner. "
        "Limit your response to one short sentence, no longer than 100 characters. "
        "Avoid unnecessary elaboration or repetition."
        )


    # Запит до моделі
    user_id = update.message.from_user.id
    context_history = memory.get_context(user_id)

    full_prompt = f"{system_prompt}\n\n{context_history}\nUser: {translated_input}\nBot:"
    response = local_model.ask(full_prompt)

    # Зберігаємо запит і відповідь
    memory.add_message(user_id, translated_input, response)

    # Переклад назад
    translated_response = translator.to_uk(response)

    await update.message.reply_text(translated_response)

# Стартова команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Напиши /ptic і своє питання чи історію.")
    
async def create_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = ' '.join(context.args)

    if not user_message:
        await update.message.reply_text(
            "Будь ласка, введіть запит для створення опитування. Приклад:\n"
            "/createpoll Якого кольору вода (чорна, зелена) anon multi"
        )
        return

    # Перевірка на анонімність та мультивибір
    anonymous = 'anon' in user_message.lower()
    multi_choice = 'multi' in user_message.lower()

    # Очистити службові слова
    cleaned_message = re.sub(r'\b(anon|multi)\b', '', user_message, flags=re.IGNORECASE).strip()

    # Витягнути запитання та варіанти
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
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ptic", process_ptic))
    app.add_handler(CommandHandler("createpoll", create_poll))
    print("Бот запущено...")
    app.run_polling()

if __name__ == '__main__':
    main()
