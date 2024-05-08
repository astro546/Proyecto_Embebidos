import serial, time
import bcrypt
from Crypto.Hash import SHA256
from cryptography.fernet import Fernet

arduino = serial.Serial('/dev/ttyUSB0', 9600)

#Carga la llave para desencriptar los hashes
def load_masterpass():
  return open("masterpass.key","rb").read()

#Desencripta los hashes de la llave para desencriptar 
# y del pin de acceso
def decrypt_file(nombre, clave):
  f = Fernet(clave)
  with open(nombre, 'rb') as file:
    encrypted_data = file.read()
  decrypted_data = f.decrypt(encrypted_data)
  return decrypted_data

#Vefifica el pin enviado por el Arduino
def verify_pin(encrypted_pin):
  masterpass = load_masterpass()
  hashedPin = decrypt_file('pinpass.key', masterpass)
  if encrypted_pin == hashedPin:
    return True
  return False

#Recibe los mensajes del Arduino  
def processMsg():
  cadena = arduino.readline()
  try:
    if cadena.decode() != '' :
      print(f"Texto recibido: {cadena.decode()}")
      if 'Timber' in cadena.decode():
        return 'T'
    return 'N'
  except UnicodeDecodeError:
    #print(f"Pin encriptado: {cadena}")
    #print(f"tamaño del texto encriptado: {len(cadena)}")
    if len(cadena) > 0:
      is_verified = verify_pin(cadena)
      if is_verified:
        command = 'W'
      else:
        command = 'D'
      return command
    return 'N'

def sendCmd(command):
  arduino.write(command.encode())

""" while True:
  processMsg() """