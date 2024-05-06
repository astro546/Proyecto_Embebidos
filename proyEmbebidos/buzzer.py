from gpiozero import Buzzer
from time import sleep

buzzer = Buzzer(12)

while True:
  sleep(1)
  buzzer.beep()
  sleep(1)