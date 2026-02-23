#include "esp_camera.h"
#include "board_config.h"
#include <WiFi.h>
#include <WebSocketsClient.h>

const char* ssid = "PLDTHOMEFIBRM764a";
const char* password = "AgotPerez@25";

const char* ws_server = "192.168.1.168";
const uint16_t ws_port = 8000;

WebSocketsClient ws;
bool stream = false;

void connectWiFi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi Connected");
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      Serial.println("WebSocket Disconnected");
      break;
    case WStype_CONNECTED:
      Serial.println("WebSocket Connected");
      break;
    case WStype_TEXT: {
      String cmd = String((char*)payload).substring(0, length);
      Serial.println("Received: " + cmd);
      if (cmd == "CAPTURE") {
        sendImageData();
      } else if (cmd == "STREAM ON") {
        stream = true;
      } else if (cmd == "STREAM OFF") {
        stream = false;
      }
      break;
    }
    default:
      break;
  }
}

void sendImageData() {
  camera_fb_t * fb = NULL;
  fb = esb_camera_fb_get();
  esp_camera_fb_return();

  fb = NULL;
  fb = esp_camera_fb_get();

  ws.sendBIN(fb->buf, fb->len);
  esp_camera_fb_return(fb);
}

void setup() {
  Serial.begin(115200);

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

  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;

  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;

  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.jpeg_quality = 10;
  config.fb_count = 2;
  config.frame_size = FRAMESIZE_QVGA;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  connectWiFi();

  ws.begin(ws_server, ws_port, "/ws");
  ws.enableHeartbeat(15000, 3000, 2);
  ws.onEvent(webSocketEvent);
  ws.setReconnectInterval(5000);
}

void loop() {
  ws.loop();

  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "CAPTURE") {
      Serial.println("Capturing image...");
      sendImageData();
    }

    if (cmd == "STREAM ON") {
      stream = true;
      Serial.println("Stream enabled");
    }

    if (cmd == "STREAM OFF") {
      stream = false;
      Serial.println("Stream disabled");
    }
  }

  if (stream) {
    sendImageData();
    delay(700);
  }
}