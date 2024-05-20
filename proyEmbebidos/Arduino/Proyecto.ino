//------------------------------------------------- Librerias utilizadas -------------------------------------------------------
#include <Keypad.h>
#include <Arduino_ST7789_Fast.h>
#include <SPI.h>
#include <Crypto.h>
#include <SHA256.h>
#include "pin_icon.h"
//------------------------------------------------------------------------------------------------------------------------------

//------------------------------------------------- Definicion de constantes ---------------------------------------------------
#define TFT_RST  9 // Pin de reset del display 
#define TFT_DC   8 // Pin de DC del display 
#define SCR_WD   240 // Ancho del display
#define SCR_HT   240 // Alto dle display
#define ORANGE   0xfd20 // Color naranja
#define PURPLE   0x5810 // Color Purpura
#define OGREEN   0x6c20 // Color verde obscuro
//------------------------------------------------------------------------------------------------------------------------------

//------------------------------------ Definicion de pines, variables y objetos ------------------------------------------------
//Definicion de variables
int timbre = 19; //Pin del boton del timbre (A5)
bool timbre_pres; //Verifica si el timbre se presiono
bool timbre_pres_bef; //Variable auxiliar para detectar el flanco de bajada del timbre
bool waiting_access = false; //Bandera de espera de la respuesta de la Raspberry Pi
bool blocked = false; //Bandera que indica si la Raspberry Pi bloqueo al Arduino
char access; //Respuesta de la Raspberry Pi
char reset; //Obtiene el comando de reset de la Raspberry Pi

//Filas y columnas del teclado matricial
const byte rowsCount = 4;
const byte columsCount = 4;

//Variables para la encriptacion de la clave de acceso
int index = 0; //Indice del pin
unsigned char pin[5]; //Buffer del pin
unsigned char hidePin[6]; //Pin oculto que se muestra en la pantalla
uint8_t hashPin[32]; //Buffer del pin hasheado

//Matriz de mapeo del teclado matricial
char keys[rowsCount][columsCount] = {
   { '1','2','3', 'A' },
   { '4','5','6', 'B' },
   { '7','8','9', 'C' },
   { '*','0','#', 'D' }
};

//Definicion de los pines del teclado matricial
const byte rowPins[rowsCount] = { 2,3,4,5};
const byte columnPins[columsCount] = { 6,7, 18,17 };

//Definicion de objetos importantes para el proyecto
Keypad keypad = Keypad(makeKeymap(keys), rowPins, columnPins, rowsCount, columsCount); //Teclado
Arduino_ST7789 tft = Arduino_ST7789(TFT_DC, TFT_RST); //Display TFT
SHA256 hash; //Hash
//------------------------------------------------------------------------------------------------------------------------------

//----------------------------------------- Funciones --------------------------------------------------------------------------
//Envia el hash del pin
void send_encrypted_pin(){
  hash.reset();
  hash.update(pin, sizeof(pin));
  hash.finalize(hashPin, sizeof(hashPin));
  for(int k=0; k<sizeof(hashPin); k++) Serial.write(hashPin[k]);
  Serial.println();
}

//Limpia el buffer del pin
void clear_pin(){
  for (int i=0; i<5 ; i++){
    pin[i] = ' ';
    hidePin[i] = ' ';
  };
  index = 0;
  tft.fillRect(30,145,175,42,WHITE);
  set_text(30,145,6,BLACK,hidePin);
}

//Obtiene la respuesta de la Raspberry Pi
char get_access(){
  char res;
  if(waiting_access && Serial.available()){
    res = Serial.read();
    bool is_res = res == 'W' || res == 'D' || res == 'B';
    //Serial.println(res);
    blocked = access == 'W' ? false : true;
    if(is_res) waiting_access = false;
    clear_pin();
    return res;
  }
  return 'N';
}

//Imprime un texto en el display
void set_text(int posx, int posy, int size, uint16_t colortext, char* text){
  tft.setCursor(posx,posy);
  tft.setTextColor(colortext);
  tft.setTextSize(size);
  tft.println(text);
}

//Imprime una alerta en el display
void set_alert(char* text, uint16_t color){
  tft.fillRect(0, 210, SCR_WD, 30, color);
  set_text(0,215,2,WHITE,text);
}

//Imprime la pantalla de la entrada del PIN
void enter_pin_screen(){
  tft.fillScreen(WHITE);
  tft.fillRect(0, 0, SCR_WD, 30, BLUE);
  set_text(5,5,3,WHITE, "PIN de Acceso");
  tft.drawImageF(90,60,64,64,pin_icon);
  for (int k=1; k<=5; k++) tft.fillRoundRect((30*k)+(5*(k-1)), 190, 30, 5, 9, BLACK);
  set_alert("Inserte su PIN", PURPLE);
}

//Maneja el evento de un boton presionado del teclado
void get_pin_key(){
  char key = keypad.getKey();

  if (key){
    if (key == '*'){
      index = index > 0 ? index - 1 : index;
      pin[index] = ' ';
      hidePin[index] = ' ';
    } else if (key == '#'){
      if(index == 5){
        send_encrypted_pin();
        set_alert("Verificando..", ORANGE);
        waiting_access = true;
      } else {
        set_alert("PIN incompleto", RED);
        delay(1000);
        set_alert("Inserte su PIN", PURPLE);
      }
    } else if (index <= 4){
      pin[index] = key;
      hidePin[index] = '*';
      index++;
    }
    //Serial.println((char*)hidePin);
    tft.fillRect(30,145,175,42,WHITE);
    set_text(30,145,6,BLACK,hidePin);
  }
}
//------------------------------------------------------------------------------------------------------------------------------

//--------------------------------------------- Setup y Loop -------------------------------------------------------------------
//Inicializa el puerto serial, timbre y display
void setup() {
  Serial.begin(9600);
  pinMode(timbre, INPUT);
  tft.init(SCR_WD, SCR_HT);
  enter_pin_screen();
  hidePin[5] = '\0';
}
 
//Bucle principal del programa
void loop() {
  //Obtenemos la tecla presionada
  get_pin_key();

  //Leemos el valor del timbre
  //Si el timbre se presiono, entonces detectamos el flanco de bajada
  //, se manda el mensaje "Timber" a la Raspberry Pi
  //y se muestra la alarta en pantalla de espera
  timbre_pres = digitalRead(timbre);
  bool falling_edge = !timbre_pres && timbre_pres_bef;
  if (falling_edge && !blocked){
    Serial.println("Timber");
    set_alert("Espere...", ORANGE);
    waiting_access = true;
  }
  timbre_pres_bef = timbre_pres;

  //Recibimos el comando enviado por la Raspberry Pi
  //Mostramos la respectiva alerta
  access = get_access();
  switch(access){
    case 'W':
      set_alert("Bienvenido", GREEN);
      break;
    case 'D':
      set_alert("Acceso denegado", RED);
      break;
    case 'B':
      set_alert("Bloqueado", RED);
      break;
    case 'N':
      break;
    default:
      break;
  }

  //Verificamos si la Raspberry Pi mando un comando de reseteo
  //En caso de que si, volvemos la pantalla a su estado original
  if(Serial.available()) reset = Serial.read();
  if(reset == 'R') {
    blocked = false;
    set_alert("Inserte su PIN", PURPLE);
    reset = ' ';
  };
}
//------------------------------------------------------------------------------------------------------------------------------