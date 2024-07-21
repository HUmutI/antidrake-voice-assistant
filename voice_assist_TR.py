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


#.env dosyasındaki api keylerini ve diğer verileri çekenzi ki kodda secret keyler falan gözükmesin.
load_dotenv()
clientID = os.getenv("CLIENT_ID")
clientSecret = os.getenv("CLIENT_SECRET")
username = os.getenv("USERNAME")
weather_api_key = os.getenv("WEATHER_API_KEY")
twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
my_phone_number = os.getenv("MY_PHONE_NUMBER") 

#izinlerin olduğu bir scope tanımlayarak bunu oauth_object'e atayıp spotipy lib'i sayesinde bi spotify objesi elde ediyoruz.
redirect_uri = 'http://google.com/callback/'
scope = 'user-modify-playback-state user-read-playback-state user-read-currently-playing'
oauth_object = spotipy.SpotifyOAuth(clientID, clientSecret, redirect_uri,scope=scope) 
token_dict = oauth_object.get_access_token() 
token = token_dict['access_token'] 
spotifyObject = spotipy.Spotify(auth=token) 
user_name = spotifyObject.current_user() 


#bu sandbox'ın numarasından benim tele mesaj gönderiyor.
#ileride görcen mesaj kaydet falan dediğimde sesi kaydedip bana wptan mesaj olarak atıyor.
def send_whatsapp_message(to, message):
    client = Client(twilio_account_sid, twilio_auth_token)
    message = client.messages.create(
        body=message,
        from_=twilio_whatsapp_number,
        to=f"whatsapp:+{to}"
    )
    return message.sid

#openweather api'ı ingilizce sonuç döndürdüğünden tr asistanda verileri trye çevirmek lazım

openweather_conditions_en = ["clear sky","few clouds","scattered clouds","broken clouds",
                             "shower rain","rain","thunderstorm","snow","mist"]

openweather_conditions_tr = ["açık gökyüzü", "az bulutlu", "parçalı bulutlu", "çok bulutlu", 
                            "sağanak yağmur", "yağmurlu", "gök gürültülü fırtına", "karlı", "sisli"]

#söylediğimiz şehir ismini query stringe koyup request atıyo eğer response code 200se hava nasıl ve kaç derece onu çekiyo api'dan
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
        return "Şehir bulunamadı. Lütfen tekrar deneyin."
    else:
        return "Hava durumu bilgisi alınamadı. Lütfen daha sonra tekrar deneyin."

#çeviri özelliği için

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
        return f"Çeviri sırasında bir hata oluştu: {e}"

#speech to text
def listen_for_command():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Komutlar dinleniyor...")
        recognizer.adjust_for_ambient_noise(source,duration=0.1)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio, language='tr-TR')
        print("Dediğiniz:", command)
        corrected_command = command.replace('İ', 'i').lower()
        return corrected_command
    except sr.UnknownValueError:
        print("Sesi anlayamadım. Lütfen tekrar deneyin.")
        return None
    except sr.RequestError:
        print("Google Ses Tanıma API'sine erişilemiyor.")
        return None

#Alperin konuşmasını sağlayan fonksiyon (text to speech)
#burda gTTS lib'i sadece mp3'ü destekliyo ama winsound lib'i de sadece wav, o yüzden response.mp3 ve response.wav oluşturuluyo aslında ikisi de aynı ses.
def respond(response_text,lang):
    print(response_text)
    tts = gTTS(text=response_text, lang=lang,slow=False)
    tts.save("response.mp3")
    sound = AudioSegment.from_mp3("response.mp3")
    speedup_sound = sound.speedup(playback_speed=1.2)
    speedup_sound.export("response.wav", format="wav")
    winsound.PlaySound("response.wav", winsound.SND_FILENAME)
    
  
def main():
    ss_count = 1
    while True:
        
        command = listen_for_command()
        #Trigger olarak Alper demek lazım. içinde alper olmayan hiçbir komutu gerçekleştirmiyor.
        triggerKeyword = "alper"

        if command and triggerKeyword in command:
            
            if "haber" in command or "nasılsın" in command or "yapıyosun" in command:
                respond("İyiyim, sen nasılsın?","tr")
                
            elif ("ekran görüntüsü" in command) or ("ss al" in command):
                pyautogui.screenshot(f"screenshot{ss_count}.png")
                ss_count += 1
                respond("Ekran görüntüsü alındı.","tr")
                
            elif "chrome" in command and "aç" in command:
                webbrowser.open("https://www.youtube.com/watch?v=JTk5pxI5loY")
                respond("Chrome'u açıyorum.","tr")
                
            elif "çevir" in command:
                respond("Çevirilecek ifadeyi söyle","tr")
                text_to_translate = listen_for_command()
                respond("Hangi dile çevirmemi istersin?","tr")
                target_language = listen_for_command()
                target_language = languages[target_language]
                translated_text = translate_text(text_to_translate, target_language)
                respond(translated_text,target_language)
                
            elif "spotify" in command and "aç" in command:
                respond("Hangi şarkıyı çalmamı istersin?","tr")
                search_song = listen_for_command()
                if "drake" in search_song:
                    search_song = "Not Like Us"
                results = spotifyObject.search(search_song, 1, 0, "track") 
                songs_dict = results['tracks'] 
                song_items = songs_dict['items'] 
                song = song_items[0]['external_urls']['spotify'] 
                respond("şarkı açılıyor","tr")
                webbrowser.open(song)
                
            elif "şarkı" in command and "dur" in command:
                spotifyObject.pause_playback()
                respond("Şarkı durduruldu.","tr")
            
            elif "şarkı" in command and "devam" in command:
                spotifyObject.start_playback()
                respond("Devam ediyor.","tr")
                
            elif "şarkı" in command and "geç" in command:
                spotifyObject.next_track()
                respond("Şarkı atlandı","tr") 
                
            elif "kaydet" in command:
                respond("Mesajın nedir?","tr")
                message = listen_for_command()
                if message:
                    send_whatsapp_message(my_phone_number, message)
                    respond("Whatsapp'ına mesaj gönderildi.","tr")
            
            elif "ara" in command:
                respond("Ne aramak istersin?","tr")
                search_query = listen_for_command()
                if search_query:
                    url = f"https://www.google.com/search?q={search_query}"
                    respond("Arama yapılıyor","tr")
                    webbrowser.open(url)
                    
            elif "hava durumu" in command:
                respond("Hangi şehrin hava durumunu öğrenmek istersin?","tr")
                city = listen_for_command()
                if city:
                    weather_info = get_weather(city)
                    respond(weather_info,"tr")
                    
            elif "çıkış" in command:
                respond("Hoşça kal!","tr")
                break
            elif "bilgisayar" in command and "kapat" in command:
                respond("Emin misin","tr")
                decision = listen_for_command()
                if "evet" in decision:
                    os.system("shutdown /s /t 1") 
                else:
                    pass

            
            else:
                respond("Anlayamadım.","tr")

if __name__ == "__main__":
    respond("Selam ben alper","tr")
    main()
