#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoWebsockets.h>
#include <ArduinoJson.h>

#include "esp_timer.h"
#include "img_converters.h"
#include "fb_gfx.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include "driver/gpio.h"

// AI Thinker Camera pins
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ===================== CONNECTION INFO =====================

const char* ssid            = "PLDTHOMEFIBRM764a";
const char* password        = "AgotPerez@25";
const char* server_host     = "192.168.1.168";
const uint16_t server_port  = 8000;

using namespace websockets;
WebsocketsClient streamClient;
WebsocketsClient eventClient;

bool stream = false;

// ===================== CAMERA SETUP =====================

esp_err_t init_camera() {
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
  config.frame_size = FRAMESIZE_QVGA;
  config.jpeg_quality = 12;
  config.fb_count = 2;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) return err;

  sensor_t * s = esp_camera_sensor_get();
  s->set_framesize(s, FRAMESIZE_QVGA);

  return ESP_OK;
}

// ===================== WIFI + WS =====================

esp_err_t init_wifi_ws() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);

  // Set up message callback
  streamClient.onMessage([](WebsocketsMessage msg) {
    String message = msg.data();
    message.trim();

    if (message == "STREAM") stream = true;
    else if (message == "!STREAM") stream = false;
    else sendImageToApi(message);
  });

  bool connected = streamClient.connect(server_host, server_port, "/ws");
  if (!connected) return ESP_FAIL;

  eventClient.connect(server_host, server_port, "/ws/event");

  streamClient.send("hello from ESP32 camera stream!");
  return ESP_OK;
}

// ===================== HELPERS =====================

void sendImageToApi(String endpoint) {
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) return;

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String serverUrl = "http://" + String(server_host) + ":" + String(server_port) + endpoint;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "image/jpeg");

    int httpResponseCode = http.POST(fb->buf, fb->len);

    if (httpResponseCode > 0) {
      String response = http.getString();
      eventClient.send(response);
    }

    http.end();
    stream = true;
  }

  esp_camera_fb_return(fb);
}

void sendImageToSocket() {
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) return;

  streamClient.sendBinary((const char*) fb->buf, fb->len);
  esp_camera_fb_return(fb);
}

// ===================== SETUP + LOOP =====================

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
  Serial.begin(115200);

  init_camera();
  init_wifi_ws();
}

void loop() {
  streamClient.poll();
  eventClient.poll();

  if (stream) sendImageToSocket();
}