#include <Arduino.h>
#include <LittleFS.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>

#include <esp_camera.h>

#include <ESP32Servo.h>

#define PWDN -1
#define RESET -1
#define XCLK 15
#define SIOD 4
#define SIOC 5

//image data
#define Y9 16
#define Y8 17
#define Y7 18
#define Y6 12
#define Y5 10
#define Y4 8
#define Y3 9
#define Y2 11

//timing
#define VSYNC 6
#define HREF 7
#define PCLK 13


Servo panServo;
Servo tiltServo; 

#define panServoPin 2
#define tiltServoPin 1

int panCurrentAngle = 90;
int panNewAngle;
int panStep;

int tiltCurrentAngle =90;
int tiltNewAngle;
int tiltStep;


const char* ssid = "";
const char* password = "";


WebServer server(80);

void setup() {

  Serial.begin(115200);


  //Camera set up
  if (psramFound()) {
    Serial.println("PSRAM found");
  }

  else {
    Serial.println("PSRAM NOT found");
  }

  camera_config_t config = {};

  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;

  config.pin_d0 = Y2;
  config.pin_d1 = Y3;
  config.pin_d2 = Y4;
  config.pin_d3 = Y5;
  config.pin_d4 = Y6;
  config.pin_d5 = Y7;
  config.pin_d6 = Y8;
  config.pin_d7 = Y9;

  config.pin_xclk = XCLK;
  config.pin_pclk = PCLK;
  config.pin_vsync = VSYNC;
  config.pin_href = HREF;

  config.pin_sccb_sda = SIOD;
  config.pin_sccb_scl = SIOC;

  config.pin_pwdn = PWDN;
  config.pin_reset = RESET;

  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  esp_err_t err = esp_camera_init(&config);

  if (err != ESP_OK){
    Serial.printf("Camera set up failed error 0x%x\n",err);
    return;
  }

  Serial.println("Camera set up");
  
  //Web server set up
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
  
    panNewAngle = value.toInt();
    Serial.print("Pan angle is: " );
    Serial.println(panNewAngle);

    panServo.write(panNewAngle);
    
    server.send(200,"text/plain","Pan angle is: "+value);

  });

  server.on("/tilt", HTTP_GET, [](){

    String value = server.arg("angle");
  
    tiltNewAngle = value.toInt();
    Serial.print("Tilt angle is: " );
    Serial.println(tiltNewAngle);

    tiltServo.write(tiltNewAngle);

    server.send(200,"text/plain","Tilt angle is: "+value);

  });
  
  server.on("/capture", HTTP_GET, []{

    camera_fb_t *fb = esp_camera_fb_get();

    if( fb == NULL){
      server.send(500, "text/plain", "Camera capture failed");
      return;
    }

    server.send_P(200, "image/jpeg", (const char *)fb->buf, fb->len);
    
    esp_camera_fb_return(fb);

  });

  server.on("/stream", HTTP_GET, []{

    WiFiClient client = server.client();

    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: multipart/x-mixed-replace; boundary=frame");
    client.println();

    while (client.connected()) {

        camera_fb_t *fb = esp_camera_fb_get();

        if (fb == NULL) {
            break;
        }

        client.println("--frame");
        client.println("Content-Type: image/jpeg");
        client.println("Content-Length: " + String(fb->len));
        client.println();

        client.write(fb->buf, fb->len);

        client.println();

        esp_camera_fb_return(fb);
    }
});

  server.begin();


  
  panServo.attach(panServoPin);
  tiltServo.attach(tiltServoPin);  
  panServo.write(panCurrentAngle);
  tiltServo.write(tiltCurrentAngle);
  

}
  

void loop() {
  server.handleClient();

  /*

  if(tiltCurrentAngle < tiltNewAngle){

      tiltStep = 1;
    }
    else{
      tiltStep = -1;
    }

    if(panCurrentAngle < panNewAngle){

      panStep = 1;
    }
    else{
      panStep = -1;
    }

  while(panCurrentAngle != panNewAngle || tiltCurrentAngle != tiltNewAngle ){

    if(panCurrentAngle != panNewAngle){

      panCurrentAngle += panStep;
      panServo.write(panCurrentAngle);
    }

    if(tiltCurrentAngle != tiltNewAngle){

      tiltCurrentAngle += tiltStep;
      tiltServo.write(tiltCurrentAngle);
    }

    delay(10);
  }
    
    

  */
 }


  
  



