import os
import requests
import json
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Spotify API
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

# Load environment variables
load_dotenv()

# User Input
year_prompt = input("Which year do you want to travel to? Type the date in the format: YYYY-MM-DD: ")
URL = f"https://www.billboard.com/charts/hot-100/{year_prompt}/"

# Using bs4 to scrape the website
response = requests.get(URL)
website_html = response.text
soup = BeautifulSoup(website_html, "html.parser")

# Getting list of songs from scraped website
list_of_songs = soup.find_all("h3", class_="a-no-trucate", id="title-of-a-story")
songs = [song.getText().strip() for song in list_of_songs]
print(songs)

# Setting up Spotify API
scope = "playlist-modify-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope=scope,
    redirect_uri="http://example.com",
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    show_dialog=True,
    cache_path="token.txt"
))

# Getting User_id
user_id = sp.current_user()["id"]

# Setting up list of song URIs
song_uris = []
year = year_prompt.split("-")[0]
for song in songs:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# Creating a new private playlist in Spotify
playlist = sp.user_playlist_create(user=user_id, name=f"{year_prompt} Billboard 100", public=False)
playlist_add_track = sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist["id"], tracks=song_uris)

