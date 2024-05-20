import spotipy
import os
import json
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from time import sleep

def auth():
  load_dotenv()
  spotify_key = os.getenv('SPOTIFY_KEY')
  spotify_secret = os.getenv('SPOTIFY_SECRET')
  redirect_uri = os.getenv('REDIRECT_URI')

  print("autenticando")
  sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=spotify_key,
    client_secret=spotify_secret,
    redirect_uri=redirect_uri,
    scope="user-modify-playback-state user-read-playback-state user-read-private",
    open_browser=False
  ))
  return sp

def start_pause(sp, state):
  try:
    if state:
      sp.start_playback()
    else:
      sp.pause_playback()
  except:
    if state:
      sp.pause_playback()
    else:
      sp.start_playback()

def next_track(sp):
  try:
    sp.next_track()
  except:
    pass

def previous_track(sp):
  try:
    sp.previous_track()
  except:
    pass

def shuffle(sp, state):
  sp.shuffle(state)

def repeat_mode(sp, mode):
  sp.repeat(mode)

def get_current_song_info(sp):
  def ms_to_minutes(ms):
    s = str(int(ms/1000)%60).zfill(2)
    m = str(int(ms/(1000*60))%60).zfill(2)
    return f"{m}:{s}"

  try:

    repeat_states = {'off':0, 'context':1, 'track':2}
    current_playback = sp.current_playback()
    current_track_name = current_playback['item']['name']
    current_track_artist = current_playback['item']['artists'][0]['name']
    current_progress_ms = current_playback['progress_ms']
    current_duration_ms = current_playback['item']['duration_ms']
    current_progress = ms_to_minutes(current_progress_ms)
    current_duration = ms_to_minutes(current_duration_ms)
    current_is_playing = current_playback['is_playing']
    current_shuffle_state = current_playback['shuffle_state']
    current_repeat_state = repeat_states[current_playback['repeat_state']]
    
    return {
            "available": True,
            "title": f"{current_track_name} - {current_track_artist} ", 
            "progress_ms": current_progress_ms,
            "duration_ms": current_duration_ms,
            "progress": current_progress,
            "duration": current_duration,
            "is_playing": current_is_playing,
            "shuffle_state": current_shuffle_state,
            "repeat_state": current_repeat_state
            }
  
  except TypeError:
    return {
            "available": False,
            "title": f"", 
            "progress_ms": "",
            "duration_ms": "",
            "progress": "",
            "duration": "",
            "is_playing": "",
            "shuffle_state": "",
            "repeat_state": ""
            }
  
