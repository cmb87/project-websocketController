/*
https://wokwi.com/projects/360194707275211777
https://github.com/gilmaimon/ArduinoWebsockets/issues/101
https://stackoverflow.com/questions/64175514/esp32-cam-websocket-wifimulti-reconnect
https://how2electronics.com/connecting-esp32-to-amazon-aws-iot-core-using-mqtt/
https://randomnerdtutorials.com/esp32-cam-ov2640-camera-settings/

// Websockets...
// I finallyfound the answer thanks to this comment. I was using the first certificate, but the second was needed. Sorry, my bad.
// The right command is:
// $ openssl s_client -showcerts -connect websocket.org:443
openssl s_client -showcerts -connect mydomain.cloud:443 ==> use the second displayed certificate for wss!

Note: When using MQTT and Websockets together without a sufficient delay the WSS server seems to cause a problem. Either the image is to big or the delay????

*/

#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include "esp_camera.h"
#include <ArduinoJson.h>
#include <ArduinoWebsockets.h>
#include <WiFi.h>
#include <WiFiMulti.h>
#include "config.h"
#include "cameraConfig.h"



WiFiMulti wifiMulti;

// Websocket
using namespace websockets;
WebsocketsClient webSocket;
WebsocketsClient videoSocket;

struct CommandoStruct {
  long t;
  long x;
  long y;
};

struct SensorStruct {
  float r;
  float h;
  float rssi;
};

#define SENSORPUBLISHINTERVAL 500

SensorStruct sensorState;

// Motor
#define A1A 14
#define A1B 15 // Motor B pins
#define B1A 13
#define B1B 2 // Motor B pins


// Timers
unsigned long t0;
unsigned long t1;
unsigned long t2;

// ======================================================
// Motors
// ======================================================

void setMotorSpeed(int pinA, int pinB, int speed) {

  int direction = 0;

  if (speed>0) {
    direction = 1;
    analogWrite(pinA, 0);  
    analogWrite(pinB, abs(speed));  
  } else if (speed<0){
    direction = -1;
    analogWrite(pinA, abs(speed));  
    analogWrite(pinB, 0);  
  } else {
    analogWrite(pinA, 0);
    analogWrite(pinB, 0); 
  }

  speed = abs(speed);
  Serial.print("Motor: ");
  Serial.print(speed);
  Serial.print(" Direction: ");
  Serial.print(direction);
  Serial.println();

}

// ======================================================
// Camera
// ======================================================
void sendFrame(){
  //capture a frame
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
      Serial.println("Frame buffer could not be acquired");
      return;
  }
  //replace this with your own function
  videoSocket.sendBinary((const char *)fb->buf, fb->len);

  //return the frame buffer back to be reused
  esp_camera_fb_return(fb);
}

// ======================================================
// Websocket
// ======================================================
// Callback function to handle WebSocket events

void onMessageCallback(WebsocketsMessage message) {
  // Handle WebSocket messages received from the server
  // Parse and deserialize JSON using ArduinoJson
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, message.data());

  if (error) {
    Serial.print("JSON deserialization failed: ");
    Serial.println(error.c_str());
    return;
  }

  // Extract data from JSON
  CommandoStruct cmds;
  cmds.t = doc["t"].as<long>();
  cmds.x = doc["x"].as<long>();
  cmds.y = doc["y"].as<long>();


  // Parse the message data into the struct
  Serial.print("t: ");
  Serial.print(cmds.t);
  Serial.print(" x:");
  Serial.print(cmds.x);
  Serial.print(" y:");
  Serial.print(cmds.y);
  Serial.println();

  if (cmds.t == 0) {

    int leftPWM = constrain(cmds.y - cmds.x/2, -255, 255);
    int rightPWM = constrain(cmds.y + cmds.x/2, -255, 255);

    setMotorSpeed(A1A, A1B, leftPWM);
    setMotorSpeed(B1B, B1A, rightPWM);

  } 
  else if (cmds.t == 1) {
    digitalWrite(BUILTIN_LED, HIGH); 
    Serial.println("Lights on");
  }
  else if (cmds.t == 2) {
    digitalWrite(BUILTIN_LED, LOW); 
    Serial.println("Lights off");
  }
}


void onEventsCallback(WebsocketsEvent event, String data) {
    if(event == WebsocketsEvent::ConnectionOpened) {
        Serial.println("Connnection Opened");
    } else if(event == WebsocketsEvent::ConnectionClosed) {
        Serial.println("Connnection Closed");
    } else if(event == WebsocketsEvent::GotPing) {
        Serial.println("Got a Ping!");
    } else if(event == WebsocketsEvent::GotPong) {
        Serial.println("Got a Pong!");
    }
}


void connectWebSocket() {

  Serial.print("Connecting to ");
  Serial.println(WEBSOCKET_SERVER);

  // Set up the WebSocket client
  webSocket.onEvent(onEventsCallback);
  webSocket.onMessage(onMessageCallback);

  if (webSocket.connect(WEBSOCKET_SERVER)) {
    Serial.println("WebSocket connected!");
  } else {
    Serial.println("WebSocket connection failed!");
  }

  // Video Socket
  // Set up the Video WebSocket client
  Serial.print("Connecting to ");
  Serial.println(WEBSOCKETVIDEO_SERVER);

  videoSocket.onEvent(onEventsCallback);
  if (videoSocket.connect(WEBSOCKETVIDEO_SERVER)) {
    Serial.println("Video WebSocket connected!");
  } else {
    Serial.println("Video WebSocket connection failed!");
  }

  

}

void sendJsonData() {
  // Create a JSON document using ArduinoJson
  StaticJsonDocument<256> doc;
  doc["r"] = sensorState.r;
  doc["h"] = sensorState.h;
  doc["rssi"] = sensorState.rssi;
  // Convert the JSON document to a string
  String jsonString;
  serializeJson(doc, jsonString);

  // Send the JSON string over the WebSocket
  webSocket.send(jsonString);
}


// ======================================================
// Setup
// ======================================================
void setup() {

  Serial.begin(115200);

  // ---------------- Wifi ----------------
  WiFi.mode(WIFI_STA);
  wifiMulti.addAP(WIFI_SSID1, WIFI_PASSWORD1);
  wifiMulti.addAP(WIFI_SSID2, WIFI_PASSWORD2);
  wifiMulti.addAP(WIFI_SSID3, WIFI_PASSWORD3);


  Serial.println("Connecting to Wi-Fi");
 
  // Connect to Wi-Fi using wifiMulti (connects to the SSID with strongest connection)
  Serial.println("Connecting Wifi...");
  if(wifiMulti.run() == WL_CONNECTED) {
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
  }

  // ---------------- Websocket ----------------
  connectWebSocket();

  // ---------------- Timers ----------------
  t0 = millis();
  t1 = millis();
  t2 = millis();

  // ---------------- Light ----------------
  pinMode(BUILTIN_LED, OUTPUT);     // Initialize the BUILTIN_LED pin as an output


  // ---------------- Camera ----------------
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // init with high specs to pre-allocate larger buffers
  // FRAMESIZE_UXGA (1600 x 1200)
  // FRAMESIZE_QVGA (320 x 240)
  // FRAMESIZE_CIF (352 x 288)
  // FRAMESIZE_VGA (640 x 480)
  // FRAMESIZE_SVGA (800 x 600)
  // FRAMESIZE_XGA (1024 x 768)
  // FRAMESIZE_SXGA (1280 x 1024)

  if(psramFound()){
    Serial.println("PSRAM found!");
    config.frame_size = FRAMESIZE_QVGA; // FRAMESIZE_SXGA;
    config.jpeg_quality = 10;  //0-63 lower number means higher quality
    config.fb_count = 2;
  } else {
    Serial.println("Using Default");
    config.frame_size = FRAMESIZE_QVGA; //FRAMESIZE_SVGA;
    config.jpeg_quality = 10;  //0-63 lower number means higher quality
    config.fb_count = 1;
  }
  
  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    delay(1000);
    ESP.restart();
  }

  camera_fb_t * fb = NULL;
  fb = esp_camera_fb_get();
  if(!fb) {
    Serial.println("Camera capture failed");
    delay(1000);
    ESP.restart();
  }

  // Configure
  sensor_t * s = esp_camera_sensor_get();
  s->set_brightness(s, 0);     // -2 to 2
  s->set_contrast(s, 0);       // -2 to 2
  s->set_saturation(s, 0);     // -2 to 2
  s->set_special_effect(s, 2); // 0 to 6 (0 - No Effect, 1 - Negative, 2 - Grayscale, 3 - Red Tint, 4 - Green Tint, 5 - Blue Tint, 6 - Sepia)
  s->set_whitebal(s, 1);       // 0 = disable , 1 = enable
  s->set_awb_gain(s, 1);       // 0 = disable , 1 = enable
  s->set_wb_mode(s, 1);        // 0 to 4 - if awb_gain enabled (0 - Auto, 1 - Sunny, 2 - Cloudy, 3 - Office, 4 - Home)
  s->set_exposure_ctrl(s, 1);  // 0 = disable , 1 = enable
  s->set_aec2(s, 0);           // 0 = disable , 1 = enable
  s->set_ae_level(s, 0);       // -2 to 2
  s->set_aec_value(s, 300);    // 0 to 1200
  s->set_gain_ctrl(s, 1);      // 0 = disable , 1 = enable
  s->set_agc_gain(s, 0);       // 0 to 30
  s->set_gainceiling(s, (gainceiling_t)0);  // 0 to 6
  s->set_bpc(s, 0);            // 0 = disable , 1 = enable
  s->set_wpc(s, 1);            // 0 = disable , 1 = enable
  s->set_raw_gma(s, 1);        // 0 = disable , 1 = enable
  s->set_lenc(s, 1);           // 0 = disable , 1 = enable
  s->set_hmirror(s, 0);        // 0 = disable , 1 = enable
  s->set_vflip(s, 0);          // 0 = disable , 1 = enable
  s->set_dcw(s, 1);            // 0 = disable , 1 = enable
  s->set_colorbar(s, 0);       // 0 = disable , 1 = enable

  Serial.println("Camera setup :)");

  // ---------------- Motors ----------------
  pinMode(A1A, OUTPUT);
  pinMode(A1B, OUTPUT);
  pinMode(B1A, OUTPUT);
  pinMode(B1B, OUTPUT);
  digitalWrite(A1A, LOW);
  digitalWrite(A1B, LOW);
  digitalWrite(B1A, LOW);
  digitalWrite(B1B, LOW);

  Serial.println("System ready :)");

}


// ======================================================
// Loop
// ======================================================
void loop() {

  // let the websockets client check for incoming messages
  if(webSocket.available()) {
    webSocket.poll();
  }

  // Video Socket
  if(videoSocket.available()) {
    videoSocket.poll();
  }

  // State Publish
  if ( millis()-t0 > SENSORPUBLISHINTERVAL ) {

    sensorState.r = 100;
    sensorState.h = 90;
    sensorState.rssi = WiFi.RSSI();
    sendJsonData();
    t0 = millis();
  }

  // Camera frame
  sendFrame();
  delay(10);

}


