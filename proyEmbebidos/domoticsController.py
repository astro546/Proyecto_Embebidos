import RPi.GPIO as GPIO  
from time import sleep
import Adafruit_DHT

#Definicion de pines
gas_sensor_pin = 23
temp_sensor_pin = 27
fan_pin = 4
main_door = 17
dog_door = 18
dog_food = 22
led_pin = 21

GPIO.setup(temp_sensor_pin, GPIO.IN)

#El servomotor controlara las puertas
def servomotor(pin: int, action: bool):
  #Configuramos el pin a 50 Hz en PWM y un ciclo de trabajo de 0  
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(17, GPIO.OUT)  
  GPIO.setup(18, GPIO.OUT)  
  GPIO.setup(22, GPIO.OUT)
  p = GPIO.PWM(pin, 50)     
  p.start(0)               

  if pin != 22:
    # El ciclo de trabajo en 11 abre la puerta
    # En 6 cierra la puerta
    duty_cycle = 11 if action else 6
    p.ChangeDutyCycle(duty_cycle)
    sleep(0.5)

  else:
    p.ChangeDutyCycle(11)
    sleep(2)      
    p.ChangeDutyCycle(6)

  p.stop()                 
  GPIO.cleanup()           

#Sensor de temperatura que controla el ventilador
def temp_sensor():
  sensor = Adafruit_DHT.DHT11
  humidity, temperature = Adafruit_DHT.read(sensor, temp_sensor_pin)

  if humidity is not None and temperature is not None:
      return int(humidity), int(temperature)
  else:
      return (-1,-1)

#Sensor de gas natural
def gas_sensor():
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(gas_sensor_pin, GPIO.IN)
  gas = GPIO.input(gas_sensor_pin)
  return not gas

#Control del ventilador
def fan_control(fan_pin: int, action: bool):
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(fan_pin, GPIO.OUT)
  output = GPIO.HIGH if action else GPIO.LOW
  GPIO.output(fan_pin, output)

#Control de los LEDs
def control_led(pin:int, action: bool):
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(pin, GPIO.OUT)
  output = GPIO.HIGH if action else GPIO.LOW
  GPIO.output(pin, output)

""" while True:
  print(temp_sensor()) """
#servomotor(main_door, 0)
#fan_control(4,0)