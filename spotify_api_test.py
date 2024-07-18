import spotipy
from spotipy.oauth2 import SpotifyOAuth

client_id = 'fe939ff1bb9b425c8de31f25091a4ff6'
client_secret = 'e1ab7d67d13641cb852478f88b24d9ea'
redirect_uri = 'http://localhost:8888/callback'

scope = 'user-library-read playlist-read-private'

sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope)

auth_url = sp_oauth.get_authorize_url()
print(f"Please navigate to the following URL to authorize the application: {auth_url}")

response = input("Paste the URL you were redirected to here: ")
code = sp_oauth.parse_response_code(response)

token_info = sp_oauth.get_access_token(code)
access_token = token_info['access_token']

sp = spotipy.Spotify(auth=access_token)

playlists = sp.current_user_playlists()
for playlist in playlists['items']:
    print(playlist['name'])