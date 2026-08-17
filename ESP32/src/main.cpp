#include <Arduino.h>
#include <LittleFS.h>
#include <Wifi.h>
#include <Webserver.h>
#include <ESPmDNS.h>

//#include <ESP32Servo.h>

//Servo myservo;
//const int servoPin = 13;

const char* ssid = "";
const char* password = "";

WebServer server(80);

void setup() {
   
  Serial.begin(115200);
  
  if(!LittleFS.begin()){
    Serial.println("Little FS mount failed");
    return;
  }

  Serial.println("Little FS mount worked");

  WiFi.begin(ssid,password);
  Serial.println("Connecting to Wifi");

  while(WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }

  Serial.println("WiFi connected");

  Serial.print("Ip address:");
  Serial.println(WiFi.localIP());

  if(MDNS.begin("esp32cam")){
    Serial.println("Open http://esp32cam.local");
  }

  server.on("/", HTTP_GET, [](){

    File file = LittleFS.open("/index.html", "r");

    if(!file){
      Serial.println("File not found");
      return;
    }
    server.streamFile(file,"text/html");
    file.close();
    
  });

  server.serveStatic("/", LittleFS, "/");

  server.begin();
}
  

void loop() {
  server.handleClient();
}

