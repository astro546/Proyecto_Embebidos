#Este es el flujo principal del sistema de domotica
from luma.core.render import canvas
import time
import timber
import threading
import queue
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
option = 0
click = 0
screen, option = state_display.values()
sp_queue_in = queue.Queue(maxsize=2)
sp_queue_out = queue.Queue(maxsize=2)
click_queue = queue.Queue(maxsize=2)

def exec_func(func):
  func()

def control_spotifyThread():
  global option, screen, sp_queue_out, click_queue
  sp_repeat_state = {0:'off', 1:'context', 2:'track'}
  sp_funcs = {
    0:spotify.shuffle,
    1:spotify.previous_track,
    2:spotify.start_pause,
    3:spotify.next_track,
    4:spotify.repeat_mode,
  }
  def execute_sp_func(option, args, sp_obj=sp):
    if option in args.keys():
      sp_funcs[option](sp_obj, args[option])
    else:
      sp_funcs[option](sp_obj)

  while True:
    sp_queue_out = sp_queue_in
    state_spotify = sp_queue_out.get()
    click = click_queue.get()
    args_funcs = {
      0: not state_spotify['shuffle_state'],
      2: not state_spotify['is_playing'],
      4: sp_repeat_state[(state_spotify['repeat_state'] + 1) % 3]
    }
    if screen == 2 and click == 1:
      execute_sp_func(option, args_funcs)
      

def dom_inThread():
  global state_spotify, state_dom_in
    
  while True:
    #Obtener datos del sensor de temperatura
    #Obtener datos del sensor de gas
    #Obtener la hora y fecha
    state_spotify = spotify.get_current_song_info(sp)
    sp_queue_in.put(state_spotify)


def keyboardThread():
  global option, screen
  click = 0
  while True:
    button = kb.get_key()
    edge = button in (1,2,3,4) and button_bef == None
    if edge:
      if screen in (0,2):
        if button == 1 and option > 0:
          option -= 1
        elif button == 2 and option < 4:
          option += 1
        elif button == 3:
          click_queue.put(1)
        print(option, click)
      elif screen == 4:
        if button == 1 and option == 2:
          option = 1
        elif button == 2 and option == 1:
          option = 2
        elif button == 3:
          click_queue.put(1)
      else:
        option = 0
    button_bef = button
    click_queue.put(0)


def displayThread():
  index = 0
  global device,screen,option,sp_queue_in,option
  while True:
    state_spotify = sp_queue_in.get()
    args_screens = {
      0: (screen, state_dom_out ,option),
      1: (screen, state_dom_in),
      2: (screen, state_spotify, option, index),
      3: (screen, state_hour),
      4: option,
      5: None
    }
    #print(f"Desde hilo de display: {sp_queue_in}")
    with canvas(device) as draw:
      display.controller(draw, screen, args_screens[screen])
      index = 0 if state_display['screen'] != 2 else (index + 1) % len(state_spotify['title']) 


if __name__ == "__main__":
  threads_funcs = [dom_inThread, keyboardThread, control_spotifyThread, displayThread]
  threads = []
  for i in range(len(threads_funcs)):
    thread = threading.Thread(target=exec_func, args=(threads_funcs[i],))
    threads.append(thread)
    thread.start()

"""   for thread in threads:
    thread.join() """
    
    