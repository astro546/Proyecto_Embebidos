#Este archivo conteine las funciones que manejan la comunicacion con el Arduino
import serial, time
import bcrypt
from Crypto.Hash import SHA256
from cryptography.fernet import Fernet

arduino = serial.Serial('/dev/ttyUSB0', 9600)

#load_masterpass: Carga la llave para desencriptar los hashes
def load_masterpass():
  return open("masterpass.key","rb").read()

#decrypt_file: Desencripta los hashes de la llave para desencriptar 
# y del pin de acceso
def decrypt_file(nombre, clave):
  f = Fernet(clave)
  with open(nombre, 'rb') as file:
    encrypted_data = file.read()
  decrypted_data = f.decrypt(encrypted_data)
  return decrypted_data

#verify_pin: Vefifica el pin enviado por el Arduino
def verify_pin(encrypted_pin):
  masterpass = load_masterpass()
  hashedPin = decrypt_file('pinpass.key', masterpass)
  if encrypted_pin == hashedPin:
    return True
  return False

#processMsg: Recibe los mensajes del Arduino y retorna el comando correspondiente
#al Arduino dependiendo del PIN enviado, o la eleccion del usario en el caso 
#de que se toque el timbre
#Si el PIN enviado es correcto, o el usuario autoriza abrir la puerta en caso de que se haya tocado el timbre
#entonces el comando enviado es W, en caso contrario, es D.
#Cuando se quiere que el arduino no cambie de estado, se envia el comando N
def processMsg():
  cadena = arduino.readline()
  try:
    if cadena.decode() != '' :
      print(f"Texto recibido: {cadena.decode()}")
      if 'Timber' in cadena.decode():
        return 'T'
    return 'N'
  except UnicodeDecodeError:
    print(f"Procesando pin encriptado")
    if len(cadena) > 0:
      is_verified = verify_pin(cadena)
      if is_verified:
        command = 'W'
      else:
        command = 'D'
      return command
    return 'N'

#sendCmd: Esta funcion manda el comando retornado por processMsg al Arduino
def sendCmd(command):
  print(f"Comando enviado: {command}")
  arduino.write(command.encode())