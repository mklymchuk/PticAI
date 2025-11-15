import ollama
import time
import statistics

# Configuration
OLLAMA_MODEL = "gemma3:4b-it-qat"

# Test prompts in Ukrainian (various lengths and complexities)
TEST_PROMPTS = [
    # Short questions
    "Привіт! Як справи?",
    "Яка сьогодні погода?",
    "Що таке AI?",
    
    # Medium questions
    "Розкажи коротко про історію України",
    "Поясни різницю між Python і JavaScript",
    "Як приготувати борщ?",
    
    # Long/complex requests
    "Придумай коротку казку про дракона, який боявся висоти",
    "Поясни принцип роботи нейронних мереж простими словами",
    "Дай поради як навчитися програмувати з нуля"
]

def measure_response_time(prompt: str) -> dict:
    """Measure response time and token count for a single prompt."""
    start_time = time.time()
    
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": "Ти корисний асистент. Відповідай українською стисло."},
                {"role": "user", "content": prompt}
            ]
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        return {
            "prompt": prompt,
            "response": response['message']['content'],
            "time": response_time,
            "success": True
        }
    
    except Exception as e:
        end_time = time.time()
        return {
            "prompt": prompt,
            "error": str(e),
            "time": end_time - start_time,
            "success": False
        }

def run_benchmark():
    """Run performance benchmark on test prompts."""
    print(f"🧪 Запуск бенчмарку для {OLLAMA_MODEL}\n")
    print("=" * 70)
    
    results = []
    
    for i, prompt in enumerate(TEST_PROMPTS, 1):
        print(f"\n📝 Тест {i}/{len(TEST_PROMPTS)}")
        print(f"Запит: {prompt}")
        
        result = measure_response_time(prompt)
        results.append(result)
        
        if result['success']:
            print(f"⏱️  Час відповіді: {result['time']:.2f}s")
            print(f"📄 Відповідь: {result['response'][:100]}...")
        else:
            print(f"❌ Помилка: {result['error']}")
        
        print("-" * 70)
    
    # Calculate statistics
    successful_times = [r['time'] for r in results if r['success']]
    
    if successful_times:
        print("\n" + "=" * 70)
        print("📊 СТАТИСТИКА")
        print("=" * 70)
        print(f"✅ Успішних запитів: {len(successful_times)}/{len(TEST_PROMPTS)}")
        print(f"⏱️  Середній час: {statistics.mean(successful_times):.2f}s")
        print(f"🚀 Найшвидший: {min(successful_times):.2f}s")
        print(f"🐌 Найповільніший: {max(successful_times):.2f}s")
        print(f"📈 Медіана: {statistics.median(successful_times):.2f}s")
        
        if len(successful_times) > 1:
            print(f"📉 Стандартне відхилення: {statistics.stdev(successful_times):.2f}s")
        
        print("=" * 70)
    
    return results

def memory_check():
    """Check if Ollama model fits in memory."""
    print("\n🔍 Перевірка пам'яті...")
    try:
        import psutil
        
        # Get current memory usage
        memory = psutil.virtual_memory()
        print(f"📊 Загальна RAM: {memory.total / (1024**3):.1f} GB")
        print(f"💾 Використано: {memory.used / (1024**3):.1f} GB ({memory.percent}%)")
        print(f"✅ Доступно: {memory.available / (1024**3):.1f} GB")
        
    except ImportError:
        print("⚠️  Встановіть psutil для перевірки пам'яті: pip install psutil")

if __name__ == "__main__":
    print("🚀 Бенчмарк продуктивності Ollama\n")
    
    # Check memory first
    memory_check()
    
    # Run benchmark
    results = run_benchmark()
    
    print("\n✅ Бенчмарк завершено!")
    print("\n💡 Рекомендації:")
    
    avg_time = statistics.mean([r['time'] for r in results if r['success']])
    
    if avg_time < 2:
        print("🎉 Відмінна швидкість! Модель працює швидко для групового чату.")
    elif avg_time < 4:
        print("✅ Прийнятна швидкість для більшості випадків.")
    else:
        print("⚠️  Повільно. Розгляньте можливість:")
        print("   - Використання меншої моделі (gemma2:2b)")
        print("   - Квантизація (якщо ще не використовується)")
        print("   - Перевірка завантаження системи")