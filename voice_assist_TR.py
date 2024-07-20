import speech_recognition as sr
from gtts import gTTS
import winsound
from pydub import AudioSegment
import pyautogui
import webbrowser

def listen_for_command():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Komutlar dinleniyor...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio, language='tr-TR')
        print("Dediğiniz:", command)
        return command.lower()
    except sr.UnknownValueError:
        print("Sesi anlayamadım. Lütfen tekrar deneyin.")
        return None
    except sr.RequestError:
        print("Google Ses Tanıma API'sine erişilemiyor.")
        return None

def respond(response_text):
    print(response_text)
    tts = gTTS(text=response_text, lang='tr')
    tts.save("response.mp3")
    sound = AudioSegment.from_mp3("response.mp3")
    sound.export("response.wav", format="wav")
    winsound.PlaySound("response.wav", winsound.SND_FILENAME)

tasks = []
listeningToTask = False

def main():
    global tasks
    global listeningToTask
    ss_count = 1
    while True:
        command = listen_for_command()

        triggerKeyword = "alper"

        if command and triggerKeyword in command:
            if listeningToTask:
                tasks.append(command)
                listeningToTask = False
                respond(f"{command} görev listenize eklendi. Şu anda listenizde {len(tasks)} görev var.")
            elif "görev ekle" in command:
                listeningToTask = True
                respond("Tabii, görev nedir?")
            elif "görevleri listele" in command:
                respond("Tabii. Görevleriniz şunlar:")
                for task in tasks:
                    respond(task)
            elif ("ekran görüntüsü al" in command) or ("ss al" in command):
                pyautogui.screenshot(f"screenshot{ss_count}.png")
                ss_count += 1
                respond("Ekran görüntüsü alındı.")
            elif "chrome" in command and "aç" in command:
                webbrowser.open("https://www.youtube.com/watch?v=JTk5pxI5loY")
                respond("Chrome'u açıyorum.")
            elif "çıkış" in command:
                respond("Hoşça kal!")
                break
            else:
                respond("Anlayamadım.")

if __name__ == "__main__":
    respond("Selam ben alper")
    main()
