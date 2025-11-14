from local_llm import LocalLLM
from translator import TranslatorWrapper

# Ініціалізація
llm = LocalLLM(model_path="/Users/kola/.llama/hf_model_1B/hf_model_1B-1.2B-q8_0.gguf")
translator = TranslatorWrapper()

print("💬 Введіть питання українською (або 'exit' для виходу):\n")
while True:
    user_input = input("🧠 Ти: ")
    if user_input.lower() in {"exit", "quit"}:
        print("👋 Бувай!")
        break

    # Переклад вхідного запиту на англійську
    question_en = translator.to_en(user_input)

    # Запит до LLM
    answer_en = llm.ask(question_en)

    # Переклад відповіді назад на українську
    answer_uk = translator.to_uk(answer_en)

    print(f"🤖 Бот: {answer_uk}\n")
