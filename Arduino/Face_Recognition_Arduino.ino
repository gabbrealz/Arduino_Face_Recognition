#include <LiquidCrystal_I2C.h>
#include <WiFiS3.h>
#include <ArduinoHttpClient.h>
#include <ArduinoJson.h>
#include <ArduinoWebsockets.h>

// ===================================================================================
// COMPONENT PINS ====================================================================

#define BUTTON 2
#define GREEN_LED 3
#define RED_LED 4
#define PIEZO 5

// ===================================================================================
// CONNECTION INFO ===================================================================

char ssid[]           = "PLDTHOMEFIBRM764a";
char password[]       = "AgotPerez@25";
char server_host[]    = "192.168.1.168";
uint16_t server_port  = 8000;

// ===================================================================================
// COMPONENTS & LOGIC VARIABLES ======================================================

LiquidCrystal_I2C lcd(0x27, 16, 2);

// ===================================================================================
// HELPERS ===========================================================================

void successTone() {
    tone(PIEZO, 1200, 150);
    delay(200);
    tone(PIEZO, 1600, 200);
}

void errorTone() {
    tone(PIEZO, 300, 400);
}

// ===================================================================================
// SETUP AND LOOP ====================================================================

void setup() {

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

  Serial.begin(115200);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected");

  delay(2000);
}

void loop() {

  if (digitalRead(BUTTON) == LOW) {

    delay(50);

    if (digitalRead(BUTTON) == LOW) {
      delay(20);

      lcd.clear();
      lcd.setCursor(0,0);
      lcd.print("Capturing...");

      String endpoint = getUploadImageEndpoint();
      if (endpoint == "") {
        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print("Network error");
        
        errorTone();
        delay(2000);

        digitalWrite(RED_LED, LOW);
        lcd.clear();
        lcd.print("Ready");
        return;
      }

      wsClient.send(endpoint); // replace Serial1.print(endpoint)

      String response = "";
      unsigned long startTime = millis();

      while (millis() - startTime < 5000) {
        wsClient.poll();
        if (wsClient.available()) {
          response = wsClient.readString();
          response.trim();
          break;
        }
      }

      lcd.clear();
      lcd.print("Ready");

      delay(500);
    }
  }
}

String getUploadImageEndpoint() {

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected");
    return "";
  }

  HttpClient client;
  client.get("http://localhost:8000/image-endpoint");

  int statusCode = client.responseStatusCode();
  String response = client.responseBody();

  if (statusCode != 200) {
    Serial.print("HTTP error: ");
    Serial.println(statusCode);
    return "";
  }

  DynamicJsonDocument doc(256);
  DeserializationError error = deserializeJson(doc, response);

  if (error) {
    Serial.print("JSON parse failed: ");
    Serial.println(error.c_str());
    return "";
  }

  const char* endpoint = doc["endpoint"];
  if (endpoint == nullptr) {
    return "";
  }

  return String(endpoint);
}