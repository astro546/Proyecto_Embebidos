from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from PIL import Image
from time import sleep

#Display: SH1106 128x64
#Seteamos el puerto y la direccion de la pantalla
serial = i2c(port=1, address=0x3C)

#Seteamos la pantalla
device = sh1106(serial)

#Iconos de domotica
open_door_icon =            Image.open('icons/dom/open-door.png').convert(device.mode)
closed_door_icon =          Image.open('icons/dom/closed-door.png').convert(device.mode)
door_icon =                 Image.open('icons/dom/door.png').convert(device.mode)
open_dog_door_icon =        Image.open('icons/dom/dog-open-door.png').convert(device.mode)
closed_dog_door_icon =      Image.open('icons/dom/dog-closed-door.png').convert(device.mode)
dog_icon =                  Image.open('icons/dom/dog.png').convert(device.mode)
fan_off_icon =              Image.open('icons/dom/fan.png').convert(device.mode)
fan_on_icon =               Image.open('icons/dom/fan-on.png').convert(device.mode)
led_off_icon =              Image.open('icons/dom/led-off.png').convert(device.mode)
led_on_icon =               Image.open('icons/dom/led-on.png').convert(device.mode)
timber_icon =               Image.open('icons/dom/timbre.png').convert(device.mode)
clock_icon =                Image.open('icons/dom/clock.png').convert(device.mode)
fire_icon =                 Image.open('icons/dom/fire.png').convert(device.mode)
clima_icon =                Image.open('icons/dom/clima.png').convert(device.mode)

#Iconos de la pantalla de spotify
spotify_icon =      Image.open('icons/spotify/spotify.png').convert(device.mode)
play_icon =         Image.open('icons/spotify/play.png').convert(device.mode)
pause_icon =        Image.open('icons/spotify/pausa.png').convert(device.mode)
repeat_icon =       Image.open('icons/spotify/repetir.png').convert(device.mode)
repeat_track_icon = Image.open('icons/spotify/repetir-track.png').convert(device.mode)
not_repeat_icon =   Image.open('icons/spotify/flecha.png').convert(device.mode)
next_icon =         Image.open('icons/spotify/siguiente-pista.png').convert(device.mode)
prev_icon =         Image.open('icons/spotify/anterior-pista.png').convert(device.mode)
shuffle_icon =      Image.open('icons/spotify/barajar.png').convert(device.mode)
not_shuffle_icon =  Image.open('icons/spotify/flecha-abajo.png').convert(device.mode)

#Indicadores del menu actual
def menu_indicators(draw, screen):
    for i in range(4):
        fill_circle = None if i != screen else "white"
        draw.ellipse(
            (52+(5*i),60,55+(5*i),63), 
            fill=fill_circle, 
            outline="white", 
            width=1)

#Menu principal del sistema de domotica
#Opciones: puerta principal y del perro, comida de perros, ventilador, luz
def menu_screen(draw, args_tuple):
    screen, state, option = args_tuple
    draw.text((1,0), "Menu domotica", fill="white")
    draw.ellipse((14,18,31,36), outline="white", fill=None, width=1)
    draw.bitmap((15,20), closed_door_icon, fill="white")
    draw.bitmap((55,20), closed_dog_door_icon, fill="white")
    draw.bitmap((95,20), dog_icon, fill="white")
    draw.bitmap((35,40), fan_on_icon, fill="white")
    draw.bitmap((75,38), led_off_icon, fill="white")
    menu_indicators(draw, screen)


def temperature_screen(draw, args_tuple):
    screen, state = args_tuple
    temp_state = state['temp']
    hum_state = state['hum']

    draw.bitmap((3,8), clima_icon, fill="white")
    draw.rounded_rectangle((40,5,120,25), radius=5,outline="white",width=1)
    draw.rounded_rectangle((40,30,120,50), radius=5,outline="white",width=1)
    draw.rounded_rectangle((1,5,36,50), radius=5,outline="white",width=1)
    draw.text((45,17), "TEMP", fill="white", font_size=7)
    draw.text((45,42), "HUM", fill="white", font_size=7) 
    draw.text((80,7), "30°C", fill="white", font_size=15)
    draw.text((80,32), "10%", fill="white", font_size=15) 
    draw.text((3,39), "WARM", fill="white", font_size=9) 
    menu_indicators(draw, screen)


def spotify_screen(draw, args_tuple):
    def scrolling_text(i, title_str):
        len_title = len(title_str)
        little_str = len_title <= 16
        str_not_end = len_title - i >= 16
        if little_str:
            title_buffer = title_str
        else:
            title_buffer = title_str[i:i+16] if str_not_end else title_str[i:]+title_str[:16-(len_title-i)]
        #sleep(0.01)
        return title_buffer
    
    def draw_control_icons(draw, shuffle_state, repeat_state, play_state, option):
        x_option_left = 40+(option*17)
        x_option_right = x_option_left + 13
        shuffle_state_icon = shuffle_icon if shuffle_state else not_shuffle_icon
        repeat_state_icon = {0: not_repeat_icon, 1: repeat_icon, 2: repeat_track_icon}
        play_state_icon = pause_icon if play_state else play_icon
        draw.bitmap((42,40), shuffle_state_icon, fill="white")
        draw.bitmap((59,40), prev_icon, fill="white")
        draw.bitmap((76,40), play_state_icon, fill="white")
        draw.bitmap((93,40), next_icon, fill="white")
        draw.bitmap((110,40), repeat_state_icon[repeat_state], fill="white")
        draw.ellipse((x_option_left,37,x_option_right,52), fill=None, outline="white", width=1)

    def calc_progress_bar_len(progress_ms, duration_ms):
        interval_ms = int(duration_ms / 40)
        interval_prog = int(progress_ms / interval_ms)
        return interval_prog * 2

    screen, sp_state, option, index = args_tuple
    title = sp_state['title']
    progress = sp_state['progress']
    duration = sp_state['duration']
    progress_ms = sp_state['progress_ms']
    duration_ms = sp_state['duration_ms']
    shuffle_state = sp_state['shuffle_state']
    repeat_state = sp_state['repeat_state']
    play_state = sp_state['is_playing']
    title_buffer = scrolling_text(index,title)
    len_play_bar = calc_progress_bar_len(progress_ms, duration_ms)

    draw.bitmap((0,15), spotify_icon, fill="white")
    draw.text((40,5),title_buffer, fill="white")
    draw.text((40,20), progress, fill="white", font_size=7)
    draw.text((102,20), duration, fill="white", font_size=7)
    draw.rounded_rectangle((39,28,121,31),radius=5,outline="white", fill=None ,width=1)
    draw.line(((40,29),(40+len_play_bar,29)), fill="white" ,width=2)
    draw_control_icons(draw, shuffle_state, repeat_state, play_state, option)
    menu_indicators(draw, screen)


def hour_screen(draw, screen, state):
    draw.bitmap((0,15), clock_icon, fill="white")
    draw.rounded_rectangle((38,12,120,37),radius=5,outline="white", fill=None ,width=1)
    draw.rounded_rectangle((38,39,120,51),radius=5,outline="white", fill=None ,width=1)
    draw.text((42,5),'03:29',fill="white", font_size=30)
    draw.text((40,40),'Sab, 24-05-2024', fill="white", font_size=10)
    menu_indicators(draw)


def timber_notif(draw, option):
    draw.text((8,0), "Abrir puerta principal?", fill="white")
    draw.bitmap((40,20), door_icon, fill="white")
    draw.bitmap((70,20), timber_icon, fill="white")
    draw.rounded_rectangle((10,52,60,62), radius=5,outline="white", fill="white" ,width=1)
    draw.rounded_rectangle((70,52,120,62),radius=5,outline="white", fill=None ,width=1)
    draw.text((30,52),"Si", fill="black", font_size=9)
    draw.text((90,52),"No", fill="white", font_size=9)


def gas_notif(draw, args_tuple=None):
    draw.bitmap((0,15), fire_icon, fill="white")
    draw.text((40,5), "ALERTA!!", fill="white", font_size=20)
    draw.text((45,25), "PRESENCIA", fill="white", font_size=15)
    draw.text((55,37), "DE GAS", fill="white", font_size=15)


def controller(draw, screen, args_tuple):
    screens = {
        0: menu_screen,
        1: temperature_screen,
        2: spotify_screen,
        3: hour_screen,
        4: timber_notif,
        5: gas_notif
    }
    if screen in screens:
        if screen == 0:
            screens[screen](draw, args_tuple)
        elif screen in (1,3):
            screens[screen](draw, args_tuple)
        elif screen == 2:
            screens[screen](draw, args_tuple)
        elif screen in 4:
            screens[screen](draw, args_tuple)
        elif screen in 5:
            screens[screen](draw)
    else:
        print("Estado invalido")