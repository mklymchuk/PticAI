import ollama
import time
import statistics
import psutil # Тепер він у нас в основній логіці

# Configuration
OLLAMA_MODEL = "gemma4:e2b-it-q4_K_M"

# Тестові запити з фокусом на ваші інтереси (фронтенд та логіка)
TEST_PROMPTS = [
    "Привіт! Напиши короткий слоган для IT-інтерна.",
    "Напиши функцію на JS для валідації email.",
    "Поясни різницю між '==' та '===' у JavaScript.",
    "Напиши CSS для адаптивної картки товару.",
    "Створи JSON структуру для опису проекту на PortMaster."
]

def measure_performance(prompt: str) -> dict:
    """Вимірює розширені метрики продуктивності."""
    start_time = time.perf_counter()
    first_token_time = None
    tokens_count = 0
    
    try:
        # Використовуємо stream=True для вимірювання швидкості
        stream = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": "Ти досвідчений фронтенд-розробник. Відповідай українською, чітко і по суті."},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )
        
        full_response = ""
        for chunk in stream:
            if first_token_time is None:
                first_token_time = time.perf_counter() - start_time
            
            content = chunk['message']['content']
            full_response += content
            # Приблизний підрахунок токенів (для точнішого результату Ollama видає 'eval_count' в кінці)
            if content.strip():
                tokens_count += 1 

        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Отримуємо точні дані від Ollama (якщо доступні в останньому чанку)
        # Примітка: в останньому чанку stream зазвичай є статистика
        
        return {
            "prompt": prompt,
            "response_len": len(full_response),
            "total_time": total_time,
            "ttft": first_token_time, # Time to First Token
            "tps": tokens_count / (total_time - (first_token_time or 0)) if total_time > 0 else 0,
            "success": True
        }
    
    except Exception as e:
        return {"prompt": prompt, "error": str(e), "success": False}

def run_benchmark():
    print(f"🚀 Тестуємо: {OLLAMA_MODEL}")
    print("-" * 50)
    
    results = []
    for prompt in TEST_PROMPTS:
        print(f"📡 Запит: {prompt[:40]}...")
        res = measure_performance(prompt)
        if res["success"]:
            results.append(res)
            print(f"   ⏱️  Перший токен: {res['ttft']:.2f}s | Швидкість: {res['tps']:.1f} tok/s")
        else:
            print(f"   ❌ Помилка: {res['error']}")

    if results:
        avg_tps = statistics.mean([r['tps'] for r in results])
        avg_ttft = statistics.mean([r['ttft'] for r in results])
        
        print("\n" + "="*30)
        print(f"📊 ПІДСУМОК (Середні значення):")
        print(f"🔹 Швидкість генерації: {avg_tps:.2f} токенів/сек")
        print(f"🔹 Затримка відповіді (TTFT): {avg_ttft:.2f} сек")
        
        # Рекомендації на основі реальних цифр
        if avg_tps > 15:
            print("🟢 Стан: Ідеально. Модель літає.")
        elif avg_tps > 5:
            print("🟡 Стан: Комфортно. Читабельно в реальному часі.")
        else:
            print("🔴 Стан: Повільно. Можливо, замало VRAM.")
        print("="*30)

if __name__ == "__main__":
    run_benchmark()