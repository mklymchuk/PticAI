import ollama

# Configuration
OLLAMA_MODEL = "gemma3:4b-it-qat"

# Function to query Ollama
def ask_ollama(prompt: str) -> str:
    """Send request to Ollama and get response."""
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": "Ти корисний асистент. Відповідай українською мовою стисло та зрозуміло."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['message']['content']
    except Exception as e:
        return f"❌ Помилка: {e}"

def main():
    print(f"💬 CLI тестування Ollama ({OLLAMA_MODEL})")
    print("Введіть питання українською (або 'exit' для виходу):\n")
    
    while True:
        user_input = input("🧠 Ти: ")
        
        if user_input.lower() in {"exit", "quit", "вихід"}:
            print("👋 Бувай!")
            break
        
        if not user_input.strip():
            continue
        
        # Get response from Ollama (no translation needed!)
        answer = ask_ollama(user_input)
        print(f"🤖 Бот: {answer}\n")

if __name__ == "__main__":
    main()