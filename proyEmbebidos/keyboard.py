import RPi.GPIO as gpio

gpio.setmode(gpio.BCM)
gpio.setup(6, gpio.IN)
gpio.setup(13, gpio.IN)
gpio.setup(19, gpio.IN)
gpio.setup(26, gpio.IN)

def get_key():
  b1 = gpio.input(13)
  b2 = gpio.input(6)
  b3 = gpio.input(26)
  b4 = gpio.input(19)
  
  b1_press = not b1 and (b2 and b3 and b4)
  b2_press = not b2 and (b1 and b3 and b4)
  b3_press = not b3 and (b1 and b2 and b4)
  b4_press = not b4 and (b1 and b2 and b3)
  
  if b1_press:
    return 1;
  elif b2_press:
    return 2;
  elif b3_press:
    return 3;
  elif b4_press:
    return 4;

  return None