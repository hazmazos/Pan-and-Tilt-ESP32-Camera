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

WiFiClient streamClient;
bool streaming = false;

TaskHandle_t streamTaskHandle;

void streamTask(void *param) {

  Serial.println("Stream task started");

  while (true) {

    if (streaming && streamClient.connected()) {
      
      camera_fb_t *fb = esp_camera_fb_get();

      if(fb != NULL) {


        Serial.println("Streaming....");
        streamClient.println("--frame");
        streamClient.println("Content-Type: image/jpeg");
        streamClient.println("Content-Length: " + String(fb->len));
        streamClient.println();

        streamClient.write(fb->buf, fb->len);

        streamClient.println();

        esp_camera_fb_return(fb);
      }
    }

    else {

      streaming = false;
    }

    vTaskDelay(1);
  }
}

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

  Serial.print("Ip address:");
  Serial.println(WiFi.localIP());

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

    uint32_t startTime = micros();

    String value = request->arg("angle");
  
    int panAngle = value.toInt();
    Serial.print("Pan angle is: " );
    Serial.println(panAngle);

    panServo.write(panAngle);
    

    
    request->send(200,"text/plain","Pan angle is: "+value);

    uint32_t endTime = micros();

    Serial.println("Time difference for pan is: " + String (endTime - startTime));

  });

  server.on("/tilt", HTTP_GET, [](AsyncWebServerRequest *request){

    uint32_t startTime = micros();

    String value = request->arg("angle");
  
    int tiltAngle = value.toInt();
    Serial.print("Tilt angle is: " );
    Serial.println(tiltAngle);

    tiltServo.write(tiltAngle);
   

    
    request->send(200,"text/plain","Tilt angle is: "+value);

    uint32_t endTime = micros();

    Serial.println("Time differnce for tilt is: " + String (endTime - startTime));

  });
  
  server.on("/capture", HTTP_GET, [](AsyncWebServerRequest *request){

    uint32_t startTime = micros();

    camera_fb_t *fb = esp_camera_fb_get();

    uint32_t endTime = micros();

    if( fb == NULL){
      request->send(500, "text/plain", "Camera capture failed");
      return;
    }

    uint32_t sendStart = micros();

    AsyncWebServerResponse *response = request->beginResponse(200, "image/jpeg", fb->buf, fb->len);
    request->send(response);
    esp_camera_fb_return(fb);

    uint32_t endStart = micros();

    Serial.println("Time taken for camera capture is: " + String (endTime - startTime));
    Serial.println("Time taken for image queue is: " + String (endStart - sendStart));
    Serial.println("Jpeg size is: " + String (fb->len));

  });

 
  server.on("/stream", HTTP_GET, [](AsyncWebServerRequest *request){

    Serial.println("HANDLER CALLED");

    AsyncWebServerResponse *response = request->beginResponseStream("multipart/x-mixed-replace; boundary=frame");

    request->send(response);
    
    streaming = true;
});

  server.begin();

  xTaskCreate(streamTask, "Stream Task", 8192, NULL, 1, &streamTaskHandle);

  
  panServo.attach(panServoPin);
  tiltServo.attach(tiltServoPin);  
  panServo.write(90);
  tiltServo.write(90);
  
}
  

void loop() {
}

