import RPi.GPIO as GPIO  
from time import sleep
import Adafruit_DHT
import board
import neopixel

#Definicion de pines
gas_sensor_pin = 23
temp_sensor_pin = 27
fan_pin = 4
servo1 = 17
servo2 = 18
servo3 = 22

pixel_pin = board.D21
num_pixels = 8
ORDER = neopixel.RGB
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)

GPIO.setmode(GPIO.BCM)
GPIO.setup(gas_sensor_pin, GPIO.IN)  
GPIO.setup(temp_sensor_pin, GPIO.IN)
GPIO.setup(fan_pin, GPIO.OUT)
GPIO.setup(servo1, GPIO.OUT)  
GPIO.setup(servo2, GPIO.OUT)  
GPIO.setup(servo2, GPIO.OUT)  

#El servomotor controlara las puertas
def servomotor(pin: int):
  #Configuramos el pin a 50 Hz en PWM y un ciclo de trabajo de 0
  GPIO.setup(pin,GPIO.OUT)  
  p = GPIO.PWM(pin, 50)     
  p.start(0)               

  # Mueve el servo hacia un lado y hacia el otro 
  # Para esto se cambia el ciclo de trabajo
  p.ChangeDutyCycle(6)     
  sleep(1)                 
  p.ChangeDutyCycle(11)    
  sleep(1)

  p.stop()                 
  GPIO.cleanup()           

#Sensor de temperatura que controla el ventilador
def temp_sensor():
  sensor = Adafruit_DHT.DHT11
  humidity, temperature = Adafruit_DHT.read_retry(sensor, temp_sensor_pin)

  if humidity is not None and temperature is not None:
        print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
  else:
      print('Failed to get reading. Try again!')

#Sensor de gas natural
def gas_sensor():
  gas = GPIO.input(gas_sensor_pin)
  if not gas:
    print("Hay gas")
  else: 
    print("no hay gas")

#Control del ventilador
def fan_control():
  GPIO.output(fan_pin, GPIO.HIGH)
  sleep(10)
  GPIO.output(fan_pin, GPIO.LOW)

#Control de los LEDs
def control_led():
  pixels.fill((10, 0, 0))
  pixels.show()
