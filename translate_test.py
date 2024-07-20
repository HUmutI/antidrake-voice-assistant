from googletrans import Translator

def translate_text(text, target_language):
    translator = Translator()
    try:
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except Exception as e:
        return f"Çeviri sırasında bir hata oluştu: {e}"

while True:

    text_to_translate = input("Çevirmek istediğin kelimeyi veya cümleyi yaz: ")
    target_language = input("Hangi dile çevirilsin? (en,fr,de ...): ")
    translated_text = translate_text(text_to_translate, target_language)
    print(translated_text)
