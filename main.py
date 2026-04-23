import ollama
import re

# Використовуємо ту саму модель, що і в основному боті
OLLAMA_MODEL = "gemma4:e2b-it-q4_K_M"

def ask_ollama(prompt: str) -> str:
    """Простий запит без історії для швидкої перевірки."""
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": "Ти — Птик, працюєш у режимі терміналу. Відповідай чітко."},
                {"role": "user", "content": prompt}
            ],
            # Додаємо keep_alive, щоб не чекати завантаження моделі щоразу
            keep_alive="10m" 
        )
        content = response['message']['content']
        # Очищення від тегів думок, як і в bot.py
        clean_content = re.sub(r'<\|think\|>.*?<\|channel\|>', '', content, flags=re.DOTALL).strip()
        return clean_content
    except Exception as e:
        return f"❌ Помилка Ollama: {e}"

def main():
    print(f"🚀 Консольний режим Птика ({OLLAMA_MODEL})")
    print("Це середовище для швидких тестів. Для виходу напишіть 'вихід'.\n")
    
    while True:
        try:
            user_input = input("👤 Ви: ")
            
            if user_input.lower() in {"exit", "quit", "вихід", "exit()"}:
                print("👋 Вихід з консолі.")
                break
            
            if not user_input.strip():
                continue
            
            print("🤖 Птик: ", end="", flush=True)
            answer = ask_ollama(user_input)
            print(answer + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Перервано користувачем.")
            break

if __name__ == "__main__":
    main()