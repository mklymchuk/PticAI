from llama_cpp import Llama
import os
import time

class LocalLLM:
    def __init__(self, model_path: str, n_ctx=512, n_threads=4,
                 temperature=0.5, top_k=50, top_p=1.0,
                 system_prompt=None):
        print("🔄 Loading quantized GGUF model...")
        verbose = os.getenv("LLM_DEBUG", "0") == "1"
        self.model = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            verbose=verbose
        )
        
        # Використовуємо system_prompt або стандартний шаблон
        self.system_prompt = system_prompt or (
            "You are a helpful assistant. Respond in one short sentence (<=100 characters)."
        )
        
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p

    def configure(self, temperature=None, top_k=None, top_p=None, system_prompt=None):
        if temperature is not None:
            self.temperature = temperature
        if top_k is not None:
            self.top_k = top_k
        if top_p is not None:
            self.top_p = top_p
        if system_prompt is not None:
                self.system_prompt = system_prompt
                
    def ask(self, question: str, system_prompt: str = None) -> str:
        prompt_to_use = system_prompt if system_prompt is not None else self.system_prompt
        prompt = f"{prompt_to_use}\n\nQ: {question}\nA:"
        response = self.model(
            prompt,
            max_tokens=2500,
            temperature=self.temperature,
            top_k=self.top_k,
            top_p=self.top_p,
            stop=["\n"]
        )
        return response["choices"][0]["text"].strip()

