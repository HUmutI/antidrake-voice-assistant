# antidrake-voice-assistant

## Steps for running the code

1) Download full.7 [ffmpeg](https://www.gyan.dev/ffmpeg/builds/) and then extract the file to the C:\ as "ffmpeg". Then add "C:\ffmpeg\bin" to the Path in System Environment Variables.

2) pip install -r requirement.txt

3) To use spotify api, users must create a project and get client_id and client_secret via [Spotify for Developers](https://developer.spotify.com/). And to learn spotify username, visit [Spotify account page](https://www.spotify.com/us/account/overview/?utm_source=spotify&utm_medium=menu&utm_campaign=your_account)
4) Same steps for getting [OpenWeather Api Key](https://openweathermap.org/api)
5) For [Twilio](https://console.twilio.com/) (which is optional feature), users must create a sandbox and get sandbox number.

6) Update .env file with all these api keys and numbers 

7) When the voice_assist_en or voice_assist_tr starts, users will be redirected to a site. **Copy the URL and paste it to the terminal.** After this, your access token will be saved in .cache file. 

8) Last but not least, to learn commands for assistant just check the source code. When you try to open Drake song, you will hear **THEY NOT LIKE US**


Put the wrong label on me, I'ma get 'em dropped, ayy
antidrake voice assistant with python by HÜSEYİN UMUT IŞIK and EMİR ŞAHİN
