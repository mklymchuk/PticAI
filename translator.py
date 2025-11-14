from deep_translator import GoogleTranslator

class TranslatorWrapper:
    def __init__(self):
        self.uk_to_en = GoogleTranslator(source='uk', target='en')
        self.en_to_uk = GoogleTranslator(source='en', target='uk')

    def to_en(self, text: str) -> str:
        return self.uk_to_en.translate(text)

    def to_uk(self, text: str) -> str:
        return self.en_to_uk.translate(text)
