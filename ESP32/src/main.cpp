#include <Arduino.h>
#include <LittleFS.h>
#include <WiFi.h>
#include <WebServer.h>
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
      Serial.println("index file not found");
      return;
    }
    server.streamFile(file,"text/html");
    file.close();
    
  });

  server.on("/script.js", HTTP_GET, []{

    File file = LittleFS.open("/script.js", "r");

    if(!file){
      Serial.println("script file not found");
      return;
    }
    server.streamFile(file,"text/javascript");
    file.close();

  });

  server.on("/style.css", HTTP_GET, []{
    
    File file = LittleFS.open("/style.css","r");

    if(!file)
    {
      Serial.println("style file not found");
      return;      
    }

    server.streamFile(file,"text/css");
    file.close();


  });

  server.on("/pan", HTTP_GET, [](){

    String value = server.arg("angle");
  
    int panAngle = value.toInt();
    Serial.print("Pan angle is: " );
    Serial.println(panAngle);

    
    server.send(200,"text/plain","Pan angle is: "+value);

  });

  server.on("/tilt", HTTP_GET, [](){

    String value = server.arg("angle");
  
    int tiltAngle = value.toInt();
    Serial.print("Tilt angle is: " );
    Serial.println(tiltAngle);

    
    server.send(200,"text/plain","Tilt angle is: "+value);

  });
  

  server.begin();
}
  

void loop() {
  server.handleClient();
}

