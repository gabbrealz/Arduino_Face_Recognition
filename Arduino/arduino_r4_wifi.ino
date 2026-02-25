#include <LiquidCrystal_I2C.h>
#include <WiFiS3.h>
#include <ArduinoWebsockets.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>

// ===================================================================================
// COMPONENT PINS ====================================================================

#define BUTTON 2
#define GREEN_LED 3
#define RED_LED 4
#define PIEZO 5

// ===================================================================================
// CONNECTION INFO ===================================================================

char ssid[]             = "PLDTHOMEFIBRM764a";
char password[]         = "AgotPerez@25";
char server_host[]      = "192.168.1.168";
uint16_t mqtt_port      = 1883;

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

// ===================================================================================
// WIFI & MQTT =======================================================================

void connectWiFi(bool reconnect = false) {
    Serial.print(reconnect ? "Reconnecting to WiFi" : "Connecting to WiFi");
    while (WiFi.begin(ssid, password) != WL_CONNECTED) {
        delay(2000);
        Serial.print('.');
    }
    Serial.print("\nConnected to WiFi!");
}

void connectMQTT(bool reconnect = false) {
    Serial.print(reconnect ? "Reconnecting to MQTT" : "Connecting to MQTT");
    while (!mqttClient.connected()) {
        if (mqttClient.connect("mqttClient")) {
            mqttClient.subscribe("arduino-r4/input");
        }
        else {
            Serial.print('.');
            delay(2000);
        }
    }
    Serial.print("\nConnected to MQTT!");
}

// ===================================================================================
// APPLICATION LOGIC =================================================================

LiquidCrystal_I2C lcd(0x27, 16, 2);

bool buttonAlreadyPressed = false;
bool requestSent = false;

byte loadingStep = 0;
unsigned long loadingTimestamp = 0;

unsigned long nonBlockingDelayTimestamp = millis();

// ===================================================================================
// HELPERS ===========================================================================

void nonBlockingDelay(unsigned long duration) {
    while (millis() - nonBlockingDelayTimestamp < duration) {
        mqttClient.loop();
    }
}

void successTone() {
    tone(PIEZO, 1200, 150);
    nonBlockingDelay(200);
    tone(PIEZO, 1600, 200);
}

void errorTone() {
    tone(PIEZO, 300, 400);
}

void lcdClearRow(byte row) {
    lcd.setCursor(0,row);
    lcd.print("                ");
    lcd.setCursor(0,row);
}

void lcdPrintSuccess(String message) {
    lcd.clear();
    lcd.print("    SUCCESS");
    lcd.setCursor(0,1);
    lcd.print(message);
}

void lcdPrintError(String message) {
    lcd.clear();
    lcd.print("     ERROR");
    lcd.setCursor(0,1);
    lcd.print(message);
}

void updateLoading() {
    if (millis() - loadingTimestamp < 750) return;
    if (loadingStep == 0) {
        lcdClearRow(0);
        lcd.print("Loading");
        loadingStep++;
    }
    else if (loadingStep < 4) {
        lcd.print(".");
        loadingStep++;
    }
    else {
        loadingStep = 0;
    }
    loadingTimestamp = millis();
}

// ===================================================================================
// MQTT CALLBACK =====================================================================

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    Serial.print("MQTT message arrived");

    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, payload, length);

    if (error) {
        Serial.print("JSON failed: ");
        Serial.println(error.c_str());
        return;
    }

    const char* request = doc["req"];

    if (strcmp(request, "ATTND") == 0) {
        requestSent = false;
        lcd.clear();

        if (doc["success"].as<bool>()) {
            lcdPrintSuccess(doc["msg"]);
            digitalWrite(GREEN_LED, HIGH);
            successTone();
            nonBlockingDelay(2000);

            digitalWrite(GREEN_LED, LOW);
            lcd.clear();
            lcd.print("READY");
        }
        else {
            lcdPrintError(doc["msg"]);
            digitalWrite(RED_LED, HIGH);
            errorTone();
            nonBlockingDelay(2000);

            digitalWrite(RED_LED, LOW);
            lcd.clear();
            lcd.print("READY");
        }
    }
    else if (strcmp(request, "RGSTR") == 0) {
        requestSent = false;
        lcd.clear();

        if (doc["success"].as<bool>()) {
            lcdPrintSuccess(doc["msg"]);
            digitalWrite(GREEN_LED, HIGH);
            successTone();
            nonBlockingDelay(2000);

            digitalWrite(GREEN_LED, LOW);
            lcd.clear();
            lcd.print("READY");
        }
        else {
            lcdPrintError(doc["msg"]);
            digitalWrite(RED_LED, HIGH);
            errorTone();
            nonBlockingDelay(2000);

            digitalWrite(RED_LED, LOW);
            lcd.clear();
            lcd.print("READY");
        }
    }
}

// ===================================================================================
// SETUP & LOOP ======================================================================

void setup() {
    Serial.begin(115200);

    pinMode(BUTTON, INPUT_PULLUP);
    pinMode(GREEN_LED, OUTPUT);
    pinMode(RED_LED, OUTPUT);
    pinMode(PIEZO, OUTPUT);

    lcd.init();
    lcd.backlight();
    lcd.setCursor(0,0);
    lcd.print("Attendance");
    lcd.setCursor(0,1);
    lcd.print("System Ready");

    mqttClient.setServer(mqtt_server, 1883);
    mqttClient.setBufferSize(512);
    mqttClient.setCallback(mqttCallback);

    connectWiFi();
    connectMQTT();

    delay(1000);
}

void loop() {
    if (WiFi.status != WL_CONNECTED) connectWiFi(true);
    if (!mqttClient.connected()) connectMQTT(true);
    mqttClient.loop();

    if (requestSent) {
        updateLoading();
        return;
    }

    bool pressed = digitalRead(BUTTON) == LOW;

    if (pressed) {
        buttonAlreadyPressed = true;
    }
    else if (buttonAlreadyPressed) {
        mqttClient.publish("arduino-r4/output", "CLICK");
        requestSent = true;
        lcd.clear();
        buttonAlreadyPressed = false;
    }
}