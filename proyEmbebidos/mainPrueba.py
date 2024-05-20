#Este es el flujo principal del sistema de domotica
import threading
import queue
import domoticsController as dom
import doorSecurity as sec
import displayController as display
import keyboard as kb
import spotifyAPI as spotify
import RPi.GPIO as GPIO 
from luma.core.render import canvas
from datetime import datetime as dt
from time import sleep

#EL objeto sp autentica la cuenta de spotify del usuario
sp = spotify.auth()

#device especifica el modelo del display OLED, el cual es el SH1106
device = display.device

#Index es un indice usado al mostrar la pantalla de spotify
index = 0

block_arduino = False

#Los siguientes diccionarios gestionan el control de los estados del sistema:
#state_dom_in: Contiene el estado de los sensores de temperatura y gas
state_dom_in = {
  "temp": 0,
  "hum": 0,
  "gas": 0,
}

#state_dom_out: Contiene el estado de las puertas, el ventilador y la luz
state_dom_out = {
  "p_main":0,
  "p_dog": 0,
  "dog_food": 0,
  "fan": 0,
  "light": 0
}

#state_spotify: Contiene el estado del reproductor de spotify
state_spotify = {
  "available": False,
  "title" : '',
  "progress_ms" : '',
  "duration_ms" : '',
  "progress" : '',
  "duration" : '',
  "is_playing": '',
  "shuffle_state": '',
  "repeat_state": '',
}

#state_hour: Contiene el estado de la fecha y la hora
state_hour = {
  'hour': '',
  'date': ''
}

#state_display: Contiene el estado de la pantalla actual 
state_display = {
  "screen" : 0,
  "option" : 0,
}

#click es una variable que registra si el usuario dio un click
click = 0

#screen y option son variables que provienen de state_display
#screen es la pantalla actual que se esta mostrando en el display
#option es la opcion actual de la pantalla actual
screen, option = state_display.values()

#Las siguientes son colas que se usan para la comunicacion entre hilos:
#sp_queue_in: Esta cola comparte el estado de Spotify entre los hilos dedicados a Spotify
sp_queue_in = queue.Queue(maxsize=2)

#sp_queue_out: Esta cola es una copia de sp_queue_in. Es usada por control_spotifyThread
sp_queue_out = queue.Queue(maxsize=2)

#state_dom_in_queue: Esta cola comparte los datos de los sensores
state_dom_in_queue = queue.Queue(maxsize=2)

#click_queue: Esta cola registra si el usuario dio un click
click_queue = queue.Queue(maxsize=2)

#Las siguientes dos colas son copias de click_queue
#Estas colas compartan si el usuaio dio un click hacia:
#click_ard_queue: Arduino
#clicksp_queue: hilo click_sp_queue
click_sp_queue = queue.Queue(maxsize=2)
click_ard_queue = queue.Queue(maxsize=2)

#Esta funcion o callback sirve para ejecutar cada uno de los hilos
def exec_func(func):
  func()


#control_spotifyThread: Este hilo controla las acciones del usuario cuando
#esta en la pantalla de Spotify y aplica las acciones en la API de spotify
def control_spotifyThread():
  global option, screen, sp_queue_out, click_queue, click_sp_queue
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
    click = click_sp_queue.get()
    args_funcs = {
      0: not state_spotify['shuffle_state'],
      2: not state_spotify['is_playing'],
      4: sp_repeat_state[(state_spotify['repeat_state'] + 1) % 3]
    }
    if click == 1 and screen == 2:
      execute_sp_func(option, args_funcs)


#sp_inThread: Este hilo obteine continuamente el estado del reproductor de Spotify
def sp_inThread():
  global state_spotify
  while True:
    state_spotify = spotify.get_current_song_info(sp)
    sp_queue_in.put(state_spotify)
    #print(state_spotify)
  

#gasThread: Este hilo obtiene informacion de manera continua del sensor de gas
#Muestra una alerta en la pantalla en caso de que haya gas
def gasThread():
  global state_dom_in, state_dom_in_queue, screen
  gas_bef = True
  while True:
    gas = dom.gas_sensor()
    screen_bef = screen if screen != 5 else screen_bef
    if (not gas_bef) and gas:
      screen_bef = screen
      screen = 5
    screen = 5 if gas else screen_bef
    gas_bef = gas
    state_dom_in['gas'] = gas
    state_dom_in_queue.put(state_dom_in)


#tempThread: Este hilo obtiene informacion de manera continua del sensor de temperatura
def tempThread():
  global state_dom_in, state_dom_in_queue
  while True:
    hum, temp = dom.temp_sensor()
    state_dom_in['temp'] = temp
    state_dom_in['hum'] = hum
    state_dom_in_queue.put(state_dom_in)


#dom_outThread: Este hilo ejecuta las acciones hacia las puertas, luz y ventilador
#dependiendo de la opcion que el usuario escoja
def dom_outThread():
  global state_dom_out, state_dom_in
  def exec_dom_out(option, action):
    pin = sp_funcs[option][1]
    sp_funcs[option][0](pin, action)

  control_fan_temp = lambda x: 0 if int(x) < 23 else 1

  sp_funcs = {
    0:(dom.servomotor, dom.main_door),
    1:(dom.servomotor, dom.dog_door),
    2:(dom.servomotor, dom.dog_food),
    3:(dom.fan_control, dom.fan_pin),
    4:(dom.control_led, dom.led_pin),
  }
  options = {
    0:"p_main",
    1:"p_dog",
    2:"dog_food",
    3:"fan",
    4:"light"
  }
  temp = 0
  
  try:
    while True:
      state_fan = state_dom_out['fan'] 
      click = click_queue.get()
      if state_fan == 2:
        temp = state_dom_in['temp']
        action_fan = control_fan_temp(temp)
        exec_dom_out(3, action_fan)
      if screen == 0:
        if option == 3:
          if click == 1:
            state_dom_out['fan'] = 0 if state_dom_out['fan'] == 2 else state_dom_out['fan']+1
            state_fan = state_dom_out['fan']
            action_fan = state_fan if state_fan != 2 else control_fan_temp(temp)
            exec_dom_out(3, action_fan)        
        elif click == 1:
          action_pin = not state_dom_out[options[option]]
          exec_dom_out(option, action_pin)
          state_dom_out[options[option]] = action_pin
  except KeyboardInterrupt:
    print("Limpiando pines...")
    GPIO.cleanup()


#arduinoThread: Este hilo recibe y manda comandos hacia el Arduino
#En caso de que se toque el timbre, se mostrara una pantalla preguntando
#al usuario si desea dejar entrar o no al visitante
#Si el usuario lleva mas de 3 intentos de insertar el PIN, 
#O que el dueño de la casa no lo deje entrar, el Arduino se bloqueara
#por un tiempo, y ese tiempo incrementara dependiendo del numero de intentos
def arduinoThread():
    global screen, option, state_dom_out
    def sleepBlockArduino(secs: int):
      current_secs = 0
      while current_secs < secs:
        sleep(1)
        sec.sendCmd('N')
        current_secs += 1

    failed_retries = 0;
    timber_denied_retries = 0;
    blocked = 'N'
    while True:
      msg = sec.processMsg()
      if msg == 'W':
        dom.servomotor(dom.main_door, 1)
        state_dom_out['p_main'] = 1
        blocked = 'N'
      elif msg == 'T':
        screen = 4
        blocked = 'N'
      else:
        failed_retries += 1
        msg = 'D' if failed_retries <= 3 else 'B'
        blocked = 'P'

      if screen == 4:
        click = click_ard_queue.get()
        if click == 1:
          if option == 0:
            dom.servomotor(dom.main_door, 1)
            state_dom_out['p_main'] = 1
            msg = 'W'
            blocked = 'N'
          else:
            timber_denied_retries += 1
            msg = 'D' if timber_denied_retries <= 3 else 'B'
            blocked = 'T'
          screen = 0

      sec.sendCmd(msg)
      if failed_retries > 3 and blocked == 'P':
        sleepBlockArduino(5 * failed_retries)
      elif timber_denied_retries > 3 and blocked == 'T':
        sleepBlockArduino(5 * timber_denied_retries)
      sleep(2)
      sec.sendCmd('R')


#hourThread: Este hilo obtiene continuamente la hora y fecha 
def hourThread():
  global state_hour
  weekdays = {
    0:'Lun',
    1:'Mar',
    2:'Mie',
    3:'Jue',
    4:'Vie',
    5:'Sab',
    6:'Dom',
  }
  format_date = lambda x: str(x).zfill(2)
  while True:
    today = dt.today()
    weekday = today.weekday()
    day = format_date(today.day)
    month = format_date(today.month)
    year = today.year
    hour = format_date(today.hour)
    minute = format_date(today.minute)
    date = f"{weekdays[weekday]},{day}-{month}-{year}"
    hour = f"{hour}:{minute}"
    state_hour = {'hour': hour, 'date': date}


#keyboardThread: Este hilo obtiene los botones que el usuario esta presionando
def keyboardThread():
  global option, screen
  button_bef = None
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
          click_sp_queue.put(1)
          #print("Click presionado")
        elif button == 4:
          screen += 1
          option = 0

      elif screen == 4:
        if button == 2 and option == 0:
          option = 1
        elif button == 1 and option == 1:
          option = 0
        elif button == 3:
          #print(screen, click)
          click_ard_queue.put(1)
        
      elif screen == 1 and button == 4:
        screen += 1
        option = 0

      elif screen == 3 and button == 4:
        screen = 0
        option = 0

    button_bef = button
    click_queue.put(0)


#displayThread: Este hilo muestra el contenido de la pantalla actual en el display OLED 
def displayThread():
  index = 0
  global device,screen,option,sp_queue_in,state_spotify,state_dom_in
  while True:
    #state_dom_in = state_dom_in_queue.get()
    if screen in (1,4,5):
      state_dom_in = state_dom_in_queue.get()
    if screen == 2:
      state_spotify = sp_queue_in.get()

    args_screens = {
      0: (screen, state_dom_out ,option),
      1: (screen, state_dom_in),
      2: (screen, state_spotify, option, index),
      3: (screen, state_hour),
      4: option,
      5: None
    }
    #print(screen)
    #print(f"Desde hilo de display: {sp_queue_in}")
    with canvas(device) as draw:
      display.controller(draw, screen, args_screens[screen])
      index = 0 if screen != 2 or not state_spotify['available'] else (index + 1) % len(state_spotify['title']) 


#En el bucle principal se ejecutaran todos los hilos de manera simultanea
if __name__ == "__main__":
  threads_funcs = [tempThread, 
                   gasThread, 
                   hourThread,
                   dom_outThread, 
                   arduinoThread,
                   keyboardThread, 
                   sp_inThread, 
                   control_spotifyThread, 
                   displayThread]
  threads = []
  for i in range(len(threads_funcs)):
    thread = threading.Thread(target=exec_func, args=(threads_funcs[i],))
    threads.append(thread)
    thread.start()
    
    