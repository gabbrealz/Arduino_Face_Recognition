#include "esp_camera.h"
#include <WiFi.h>
#include <ArduinoWebsockets.h>

#include "esp_timer.h"
#include "img_converters.h"
#include "fb_gfx.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include "driver/gpio.h"

using namespace websockets;

// ===================================================================================
// AI THINKER CAMERA PINS ============================================================

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

// ===================================================================================
// CONNECTION INFO ===================================================================

const char* ssid            = "WIFI_NAME";
const char* password        = "WIFI_PASSWORD";
const char* serverHost      = "192.168.1.168";
const uint16_t serverPort   = 8000;

const char* wsEndpoint      = "/camera";

WebsocketsClient wsClient;

// ===================================================================================
// WIFI & WEBSOCKET ==================================================================

void connectWiFi(bool reconnect = false) {
    Serial.print(reconnect ? "Reconnecting to WiFi" : "Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(2000);
        Serial.print('.');
    }
    Serial.print("\nConnected to WiFi!");
}

void connectWebsocket(bool reconnect = false) {
    Serial.print(reconnect ? "Reconnecting to Websocket" : "Connecting to Websocket");
    while (!wsClient.connect(serverHost, serverPort, wsEndpoint)) {
        Serial.print('.');
        delay(2000);
    }
    Serial.print("\nConnected to Websocket!");
}

// ===================================================================================
// APPLICATION LOGIC =================================================================



// ===================================================================================
// HELPERS ===========================================================================

void sendImageToSocket() {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Image capture failed");
        return;
    }

    wsClient.sendBinary((const char*) fb->buf, fb->len);
    esp_camera_fb_return(fb);
}

// ===================================================================================
// SETUP AND LOOP ====================================================================

void setup() {
    WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
    
    Serial.begin(115200);
    while (!Serial);

    initializeCamera();

    WiFi.begin(ssid, password);
    connectWiFi();

    connectWebsocket();
}

void loop() {
    if (WiFi.status() != WL_CONNECTED) connectWiFi(true);
    if (wsClient.available()) {
        wsClient.poll();
        sendImageToSocket();
    }
    else connectWebsocket(true);
}

// ===================================================================================
// CAMERA SETUP ======================================================================

esp_err_t initializeCamera() {
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
    config.jpeg_quality = 10;
    config.fb_count = 2;
    config.grab_mode = CAMERA_GRAB_LATEST;

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.println("Camera initialization failed");
        return err;
    }

    sensor_t * s = esp_camera_sensor_get();
    s->set_framesize(s, FRAMESIZE_QVGA);

    Serial.println("Camera initialization success!");
    return ESP_OK;
}