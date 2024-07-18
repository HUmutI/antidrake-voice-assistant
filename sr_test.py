import speech_recognition as sr

r = sr.Recognizer()
print("START TO TALK \n")
while True:
    with sr.Microphone() as source:
        
        audio_text = r.listen(source)
     
        try:
            print(r.recognize_google(audio_text))
        except:
            print("Sorry, I did not get that")