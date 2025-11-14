import json
import os

class ChatMemory:
    def __init__(self, max_history=5, filepath="chat_logs.json"):
        self.max_history = max_history
        self.filepath = filepath
        self.memory = self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_memory(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)

    def add_message(self, user_id, user_msg, bot_reply):
        user_id = str(user_id)
        if user_id not in self.memory:
            self.memory[user_id] = []

        self.memory[user_id].append({"user": user_msg, "bot": bot_reply})

        # Обрізаємо до max_history
        self.memory[user_id] = self.memory[user_id][-self.max_history:]

        self._save_memory()

    def get_context(self, user_id):
        user_id = str(user_id)
        if user_id not in self.memory:
            return ""
        
        history = self.memory[user_id]
        context_lines = []
        for pair in history:
            context_lines.append(f"User: {pair['user']}")
            context_lines.append(f"Bot: {pair['bot']}")
        return "\n".join(context_lines)
