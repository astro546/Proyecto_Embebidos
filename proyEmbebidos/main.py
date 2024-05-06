#Este es el flujo principal del sistema de domotica
from luma.core.render import canvas
import time
import timber
import domoticsController as dom
#import doorSecurity as sec
import displayController as display
import keyboard as kb
import spotifyAPI as spotify

sp = spotify.auth()
device = display.device
index = 0
block_arduino = False
state_dom_in = {
  "temp": "0°C",
  "hum": "0%",
  "gas": 0,
}
state_dom_out = {
  "p_main":0,
  "p_dog": 0,
  "dog_food": 0,
  "fan": 0,
  "light": 0
}
state_spotify = {
  "title" : '',
  "progress_ms" : '',
  "duration_ms" : '',
  "progress" : '',
  "duration" : '',
  "is_playing": '',
  "shuffle_state": '',
  "repeat_state": '',
}
state_hour = {
  'hour': '',
  'date': ''
}
state_display = {
  "screen" : 2,
  "option" : 0,
}

if __name__ == "__main__":

  while True:
    # Obtiene los inputs de los sensores, botones y arduino para
    # manipular los estados
    #sec.processMsg()
    print(kb.get_key())
    state_spotify = spotify.get_current_song_info(sp)

    # Ejecuta las acciones de los servos, leds y ventilador
    # Muestra la pantalla dependiendo de los estados
    screen, option = state_display.values()
    args_screens = {
      0: (screen, state_dom_out ,option),
      1: (screen, state_dom_in),
      2: (screen, state_spotify, option, index),
      3: (screen, state_hour),
      4: option,
      5: None
    }
    with canvas(device) as draw:
      display.controller(draw, screen, args_screens[screen])
      index = 0 if state_display['screen'] != 2 else (index + 1) % len(state_spotify['title']) 
