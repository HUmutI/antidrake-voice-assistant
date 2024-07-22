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
                weather_description = openweather_conditions_en[i]
                
        weather_response = f"{weather_description} and temperature is {round((temperature-272.15),1)} degree."
        return weather_response
    elif data["cod"] == "404":
        return "City not found."
    else:
        return "Weather information could not found."

languages = {
    'arabic': 'ar',
    'chinese': 'zh-cn',
    'english': 'en',
    'french': 'fr',
    'german': 'de',
    'italian': 'it',
    'japanese': 'ja',
    'korean': 'ko',
    'latin': 'la',
    'portuguese': 'pt',
    'russian': 'ru',
    'spanish': 'es',
    'turkish': 'tr',
}

def translate_text(text, target_language):
    translator = Translator()
    try:
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except Exception as e:
        return f"An error occured: {e}"

def listen_for_command():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening for commands...")
        recognizer.adjust_for_ambient_noise(source,duration=0.1)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio, language='en-EN')
        print("Command:", command)
        corrected_command = command.replace('İ', 'i').lower()
        return corrected_command
    except sr.UnknownValueError:
        print("Could not understand.")
        return None
    except sr.RequestError:
        print("Can not reach Google Voice recognition API.")
        return None

def respond(response_text,lang = "en"):
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
        triggerKeyword = "einstein"

        if command and triggerKeyword in command:
            
            if "what's" in command or "how are you" in command or "you doing" in command:
                respond("I'am fine, what about you?")
                
            elif ("screenshot" in command):
                pyautogui.screenshot(f"screenshot{ss_count}.png")
                ss_count += 1
                respond("Screenshotted.")
                
            elif "chrome" in command and "open" in command:
                webbrowser.open("https://www.youtube.com/watch?v=JTk5pxI5loY")
                respond("Opening Chrome.")

            elif "translate" in command or "translation" in command:
                respond("Spit the words!")
                text_to_translate = listen_for_command()
                if text_to_translate.lower() == "cancel" or text_to_translate is None:
                    continue
                respond("Which language are we translating duh?")
                target_language = listen_for_command()
                if target_language.lower() == "cancel" or target_language is None:
                    continue
                target_language = languages[target_language]
                translated_text = translate_text(text_to_translate, target_language)
                respond(translated_text,target_language)
                
            elif (("spotify" in command or "song" in command) and "open" in command) or ("song" in command and "change" in command):
                if is_spotify_open:
                    spotifyObject.pause_playback()
                respond("Which song you want me to play?")
                search_song = listen_for_command()
                
                if (search_song is None) or (search_song.lower() == "cancel"):
                    continue

                if "drake" in search_song:
                    search_song = "Not Like Us"

                results = spotifyObject.search(search_song, 1, 0, "track") 
                songs_dict = results['tracks'] 
                song_items = songs_dict['items']
                song = song_items[0]['external_urls']['spotify'] 
                respond("Opening song.")
                webbrowser.open(song)
                is_spotify_open = True
            elif "song" in command and ("stop" in command or "pause" in command) :
                try:
                    spotifyObject.pause_playback()
                    respond("Song paused.")
                except Exception as e:
                    respond(f"Error occured: {e}")
                    continue
            elif "song" in command and "continue" in command:
                try:
                    spotifyObject.start_playback()
                    respond("Playing song.")
                except Exception as e:
                    respond(f"Error occurede: {e}")
                    continue
            elif "song" in command and "skip" in command:
                try:
                    spotifyObject.next_track()
                    respond("Song skipped.")
                except Exception as e:
                    respond(f"Error occured: {e}")
                    continue
                
            elif "message" in command:
                respond("What is your message?")
                message = listen_for_command()
                if message.lower() == "cancel" or message is None:
                    continue
                if message:
                    send_whatsapp_message(my_phone_number, message)
                    respond("Sent the message to your Whatsapp.")
            
            elif "search" in command:
                respond("What do you want to search?")
                search_query = listen_for_command()
                if search_query.lower() == "cancel" or search_query is None:
                    continue
                if search_query:
                    url = f"https://www.google.com/search?q={search_query}"
                    respond("Searching.")
                    webbrowser.open(url)
                    
            elif "weather" in command:
                respond("Which city would you like to know about the weather?")
                city = listen_for_command()
                if city.lower() == "cancel" or city is None:
                    continue
                if city:
                    weather_info = get_weather(city)
                    respond(weather_info)
                    
            elif "exit" in command:
                respond("See you!")
                break
            elif ("computer" in command or "pc" in command) and "close" in command:
                respond("Are you sure")
                decision = listen_for_command()
                if "yes" in decision or ("sure" in decision and "not" not in decision):
                    os.system("shutdown /s /t 1") 
                else:
                    pass

            
            else:
                respond("I could not understand.")

if __name__ == "__main__":
    respond("Hi, I am Einstein!")
    main()
