#include <Arduino.h>
#include <LittleFS.h>
#include <WiFi.h>
#include <ESPAsyncWebServer.h>
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

#define panServoPin 1
#define tiltServoPin 2

// Look into NETWIZARD 
const char* ssid = "";
const char* password = "";
AsyncWebServer server(80);

camera_fb_t *streamFrame = nullptr;
size_t streamPosition = 0;
String streamHeader;
bool streamFrameEnd = false;

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
  config.jpeg_quality = 9;
  config.fb_count = 1;

  esp_err_t err = esp_camera_init(&config);

  if (err != ESP_OK){
    Serial.printf("Camera set up failed error 0x%x\n",err);
    return;
  }

  Serial.println("Camera set up");
  
  
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

  if(MDNS.begin("esp32cam")){
    Serial.println("Open http://esp32cam.local");
  }

  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    
    request->send(LittleFS, "/index.html", "text/html");    
  });

  server.on("/script.js", HTTP_GET, [](AsyncWebServerRequest *request){

    request->send(LittleFS, "/script.js", "text/javascript");
  });

  server.on("/style.css", HTTP_GET, [](AsyncWebServerRequest *request){
  
    request->send(LittleFS, "/style.css", "text/css");

  });

  server.on("/pan", HTTP_GET, [](AsyncWebServerRequest *request){

    String value = request->arg("angle");
  
    int panAngle = value.toInt();
    Serial.print("Pan angle is: " );
    Serial.println(panAngle);

    panServo.write(panAngle);
    
    request->send(200,"text/plain","Pan angle is: "+value);
  });

  server.on("/tilt", HTTP_GET, [](AsyncWebServerRequest *request){

    String value = request->arg("angle");
  
    int tiltAngle = value.toInt();
    Serial.print("Tilt angle is: " );
    Serial.println(tiltAngle);

    tiltServo.write(tiltAngle);
   
    request->send(200,"text/plain","Tilt angle is: "+value);
  });
  
  server.on("/capture", HTTP_GET, [](AsyncWebServerRequest *request){

    camera_fb_t *fb = esp_camera_fb_get();
   
    if( fb == NULL){
      request->send(500, "text/plain", "Camera capture failed");
      return;
    }

    AsyncWebServerResponse *response = request->beginResponse(200, "image/jpeg", fb->buf, fb->len);
    request->send(response);
    esp_camera_fb_return(fb);
    
  });
 
  server.on("/stream", HTTP_GET, [](AsyncWebServerRequest *request){

    //Serial.println("HANDLER CALLED");

    AsyncWebServerResponse *response = request->beginChunkedResponse(
      "multipart/x-mixed-replace; boundary=frame",
      [](uint8_t *buffer, size_t maxLen, size_t index) -> size_t {

        if(streamFrameEnd){
          
          if(maxLen < 2){
            return 0;
          }

          buffer[0] = '\r';
          buffer[1] = '\n';

          esp_camera_fb_return(streamFrame);
          streamFrame = nullptr;

          streamPosition = 0;
          streamHeader = "";
          streamFrameEnd = false;

          return 2;
        }

        // get new frame when needed
        if(streamFrame == nullptr){
          
          streamFrame = esp_camera_fb_get();

          
          if(streamFrame == nullptr){
            
            //Serial.println("Frame capture failed");
            return 0;
          }
          
          streamPosition = 0;

          streamHeader =
          "--frame\r\n"
          "Content-type: image/jpeg\r\n"
          "Content-length: " + String(streamFrame->len) + "\r\n\r\n";
          //Serial.println("Frame capture worked");
        }

        size_t bytesToSend = 0;

        // check if we sent all the header yet or stil have to
        if(streamPosition < streamHeader.length()){

          size_t headerRemaining = streamHeader.length() - streamPosition;
          //cant send anymore at a time
          bytesToSend = min(headerRemaining, maxLen);
          // send total in max parts possible
          memcpy(buffer, streamHeader.c_str() + streamPosition, bytesToSend);
          streamPosition += bytesToSend;
          
        }

        // header sent now jpeg
        else{

          size_t jpegPosition = streamPosition - streamHeader.length();
          size_t jpegRemaining = streamFrame->len - jpegPosition;

          bytesToSend = min(jpegRemaining, maxLen);

          memcpy(buffer, streamFrame->buf + jpegPosition, bytesToSend);
          streamPosition += bytesToSend;

          if(jpegPosition + bytesToSend >= streamFrame->len){

            streamFrameEnd = true;
          }
        }
        
        return bytesToSend;        
      });

      request->send(response);
});

  server.begin();

  panServo.attach(panServoPin);
  tiltServo.attach(tiltServoPin);  
  panServo.write(90);
  tiltServo.write(90);
  
}
  

void loop() {
}

