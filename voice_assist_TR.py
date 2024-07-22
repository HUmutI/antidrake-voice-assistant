import speech_recognition as sr
from gtts import gTTS
import winsound
from pydub import AudioSegment
import pyautogui
import webbrowser
import spotipy 
from dotenv import load_dotenv
import os
import requests
from twilio.rest import Client
from googletrans import Translator 
import os

load_dotenv()
clientID = os.getenv("CLIENT_ID")
clientSecret = os.getenv("CLIENT_SECRET")
username = os.getenv("USERNAME")
weather_api_key = os.getenv("WEATHER_API_KEY")
twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
my_phone_number = os.getenv("MY_PHONE_NUMBER") 

redirect_uri = 'http://google.com/callback/'
scope = 'user-modify-playback-state user-read-playback-state user-read-currently-playing'
oauth_object = spotipy.SpotifyOAuth(clientID, clientSecret, redirect_uri,scope=scope) 
token_dict = oauth_object.get_access_token() 
token = token_dict['access_token'] 
spotifyObject = spotipy.Spotify(auth=token) 
user_name = spotifyObject.current_user() 

def send_whatsapp_message(to, message):
    client = Client(twilio_account_sid, twilio_auth_token)
    message = client.messages.create(
        body=message,
        from_=twilio_whatsapp_number,
        to=f"whatsapp:+{to}"
    )
    return message.sid

openweather_conditions_en = ["clear sky","few clouds","scattered clouds","broken clouds",
                             "shower rain","rain","thunderstorm","snow","mist"]

openweather_conditions_tr = ["açık gökyüzü", "az bulutlu", "parçalı bulutlu", "çok bulutlu", 
                            "sağanak yağmur", "yağmurlu", "gök gürültülü fırtına", "karlı", "sisli"]

def get_weather(city):
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}"
    response = requests.get(base_url)
    data = response.json()
    print(data)
    if response.status_code == 200:
        main = data["main"]
        weather = data["weather"][0]
        temperature = int(main["temp"])
        weather_description = weather["description"]
        for i in range(len(openweather_conditions_en)):
            if openweather_conditions_en[i] == weather_description:
                weather_description = openweather_conditions_tr[i]
                
        weather_response = f"{weather_description} ve sıcaklık {round((temperature-272.15),1)} derece."
        return weather_response
    elif data["cod"] == "404":
        return "Şehir bulunamadı."
    else:
        return "Havadurumu bilgisi bulunamadı."

languages = {
    'arapça': 'ar',
    'çince': 'zh-cn',
    'ingilizce': 'en',
    'fransızca': 'fr',
    'almanca': 'de',
    'italyanca': 'it',
    'japonca': 'ja',
    'korece': 'ko',
    'latince': 'la',
    'portekizce': 'pt',
    'rusça': 'ru',
    'ispanyolca': 'es',
    'türkçe': 'tr',
}

def translate_text(text, target_language):
    translator = Translator()
    try:
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except Exception as e:
        return f"Bir hata oluştu: {e}"

def listen_for_command():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Komut dinleniyor...")
        recognizer.adjust_for_ambient_noise(source,duration=0.1)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio, language='tr-TR')
        print("Komut:", command)
        corrected_command = command.replace('İ', 'i').lower()
        return corrected_command
    except sr.UnknownValueError:
        print("Anlayamadım.")
        return None
    except sr.RequestError:
        print("Ulaşılamıyor: Google Voice recognition API.")
        return None

def respond(response_text,lang = "tr"):
    print(response_text)
    tts = gTTS(text=response_text, lang=lang,slow=False)
    tts.save("response.mp3")
    sound = AudioSegment.from_mp3("response.mp3")
    speedup_sound = sound.speedup(playback_speed=1.2)
    speedup_sound.export("response.wav", format="wav")
    winsound.PlaySound("response.wav", winsound.SND_FILENAME)
    
def main():
    is_spotify_open = False
    ss_count = 1
    while True:
        
        command = listen_for_command()
        triggerKeyword = "alper"

        if command and triggerKeyword in command:
            
            if "haber" in command or "nasılsın" in command or "yapıyorsun" in command:
                respond("İyiyim sen nasılsın?")
                
            elif ("screenshot" in command or "ekran görüntüsü" in command):
                pyautogui.screenshot(f"screenshot{ss_count}.png")
                ss_count += 1
                respond("Ekran görüntüsü alındı.")
                
            elif "chrome" in command and "aç" in command:
                webbrowser.open("https://www.youtube.com/watch?v=JTk5pxI5loY")
                respond("Chrome açılıyor.")

            elif "çevir" in command :
                respond("Çevirilicek metini söyle: ")
                text_to_translate = listen_for_command()
                if text_to_translate.lower() == "iptal" or text_to_translate is None:
                    continue
                respond("Hangi dile çevirmek istiyorsun?")
                target_language = listen_for_command()
                if target_language.lower() == "iptal" or target_language is None:
                    continue
                target_language = languages[target_language]
                translated_text = translate_text(text_to_translate, target_language)
                respond(translated_text,target_language)
                
            elif (("spotify" in command or "şarkı" in command) and "aç" in command) or ("şarkı" in command and "değiş" in command):
                if is_spotify_open:
                    spotifyObject.pause_playback()
                respond("Hangi şarkıyı çalmak istiyorsun?")
                search_song = listen_for_command()
                
                if (search_song is None) or (search_song.lower() == "iptal"):
                    continue

                if "drake" in search_song:
                    search_song = "Not Like Us"

                results = spotifyObject.search(search_song, 1, 0, "track") 
                songs_dict = results['tracks'] 
                song_items = songs_dict['items']
                song = song_items[0]['external_urls']['spotify'] 
                respond("Şarkı açılıyor.")
                webbrowser.open(song)
                is_spotify_open = True

            elif "şarkı" in command and "dur" in command:
                try:
                    spotifyObject.pause_playback()
                    respond("Şarkı durduruldu.","tr")
                except Exception as e:
                    respond(f"Hata oluştu: {e}")
                    continue
            elif "şarkı" in command and "devam" in command:
                try:
                    spotifyObject.start_playback()
                    respond("Şarkı devam ettiriliyor.","tr")
                except Exception as e:
                    respond(f"Hata oluştu: {e}")
                    continue
            elif "şarkı" in command and "geç" in command:
                try:
                    spotifyObject.next_track()
                    respond("Şarkı geçildi.","tr")
                except Exception as e:
                    respond(f"Hata oluştu: {e}")
                    continue
            elif "mesaj" in command:
                respond("Mesajın nedir?")
                message = listen_for_command()
                if message.lower() == "iptal" or message is None:
                    continue
                if message:
                    send_whatsapp_message(my_phone_number, message)
                    respond("Mesaj Whatsapp'ına gönderildi.")
            
            elif "ara" in command:
                respond("Ne aramak istiyorsun?")
                search_query = listen_for_command()
                if search_query.lower() == "iptal" or search_query is None:
                    continue
                if search_query:
                    url = f"https://www.google.com/search?q={search_query}"
                    respond("Arama yapılıyor.")
                    webbrowser.open(url)
                    
            elif "hava" in command:
                respond("Hangi şehrin hava durumunu öğrenmek istiyorsun?")
                city = listen_for_command()
                if city.lower() == "iptal" or city is None:
                    continue
                if city:
                    weather_info = get_weather(city)
                    respond(weather_info)
                    
            elif "çık" in command:
                respond("Görüşürüz!")
                break
            elif ("bilgisayar" in command or "pc" in command) and "kapat" in command:
                respond("Emin misin?")
                decision = listen_for_command()
                if "evet" in decision or ("emin" in decision and "değil" not in decision):
                    os.system("shutdown /s /t 1") 
                else:
                    pass

            
            else:
                respond("Anlayamadım.")

if __name__ == "__main__":
    respond("Merhaba ben Alper!")
    main()
