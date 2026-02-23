#define MQTT_MAX_PACKET_SIZE 4096

#include "esp_camera.h"
#include "board_config.h"
#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASSWORD";

const char* mqtt_server = "IP_HOSTING_MQTT_SERVER";
const int mqtt_port = 1883;

WiFiClient wifi;
PubSubClient client(wifi);

bool stream = false;

void connectWiFi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void connectMQTT() {
  while (!client.connected()) {
    if (client.connect("esp32cam")) {
      client.subscribe("esp32/capture");
    } else {
      delay(2000);
    }
  }
}

void sendImageData(char* topic) {
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) return;
  
  client.publish(topic, "START");

  const size_t chunkSize = 1024;

  for (size_t i = 0; i < fb->len; i += chunkSize) {
    size_t len = (i + chunkSize > fb->len) ? fb->len - i : chunkSize;
    client.publish(topic, fb->buf + i, len);
    delay(10);
  }

  client.publish(topic, "END");
  esp_camera_fb_return(fb);
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {

  String cmd;
  for (unsigned int i = 0; i < length; i++) {
    cmd += (char)payload[i];
  }

  if (cmd == "CAPTURE") {
    sendImageData("camera/capture");
  }
  else if (cmd == "STREAM ON") {
    stream = true;
  }
  else if (cmd == "STREAM OFF") {
    stream = false;
  }

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
  config.frame_size = FRAMESIZE_HQVGA;
  config.jpeg_quality = 15;
  config.fb_count = psramFound() ? 2 : 1;

  esp_camera_init(&config);

  connectWiFi();

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqttCallback);

  connectMQTT();
}

void loop() {
  if (!client.connected()) {
    connectMQTT();
  }
  else if (stream) {
    sendImageData("camera/stream")
  }

  client.loop();
}