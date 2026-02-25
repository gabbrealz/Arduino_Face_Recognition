#include <LiquidCrystal_I2C.h>
#include <WiFiS3.h>
#include <ArduinoWebsockets.h>
#include <ArduinoJson.h>
#include <MQTT.h>

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
char mqttServer[]       = "192.168.1.168";
uint16_t mqttPort       = 1883;

WiFiClient wifiClient;
MQTTClient mqttClient;

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
        if (mqttClient.connect("arduino-r4")) {
            mqttClient.subscribe("arduino-r4/input", 1);
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

unsigned long lastRequestTimestamp = 0;
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
    unsigned long now = millis();

    if (now - loadingTimestamp < 750) return;
    if (now - lastRequestTimestamp >= 12000) {
        requestSent = false;
        lcdPrintError("No response");
    }

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

void mqttCallback(String &topic, String &payload) {
    Serial.print("MQTT message arrived");

    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, payload.c_str());

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

    mqttClient.setServer(mqttServer, mqttPort);
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
    else if (buttonAlreadyPressed && millis() - lastRequestTimestamp > 2000) {
        mqttClient.publish("arduino-r4/output", "CLICK", false, 1);
        requestSent = true;
        lcd.clear();
        
        buttonAlreadyPressed = false;
        lastRequestTimestamp = millis();
    }
}