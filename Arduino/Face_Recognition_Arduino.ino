#include <WiFiS3.h>
#include <ArduinoHttpClient.h>
#include <ArduinoJson.h>

#define BUTTON 2
#define GREEN_LED 3
#define RED_LED 4
#define PIEZO 5

char serverAddress[] = "192.168.1.168";
int port = 8000;

WiFiClient wifi;
HttpClient client = HttpClient(wifi, serverAddress, port);

LiquidCrystal_I2C lcd(0x27, 16, 2);

void successTone() {
  tone(PIEZO, 1200, 150);
  delay(200);
  tone(PIEZO, 1600, 200);
}

void errorTone() {
  tone(PIEZO, 300, 400);
}

void setup() {

  pinMode(BUTTON, INPUT_PULLUP);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(PIEZO, OUTPUT);

  Serial1.begin(115200);   // communication with ESP32

  lcd.init();
  lcd.backlight();

  lcd.setCursor(0,0);
  lcd.print("Attendance");
  lcd.setCursor(0,1);
  lcd.print("System Ready");

  Serial1.print("STREAM");

  delay(2000);
}

void loop() {

  if (digitalRead(BUTTON) == LOW) {

    delay(50);

    if (digitalRead(BUTTON) == LOW) {

      Serial1.print("!STREAM");
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

      Serial1.print(endpoint);

      String response = "";
      unsigned long startTime = millis();

      while (millis() - startTime < 5000) {
        if (Serial1.available()) {
          response = Serial1.readStringUntil('\n');
          response.trim();
          break;
        }
      }

      if (response == "") {
        digitalWrite(RED_LED, HIGH);

        lcd.clear();
        lcd.print("Camera Error");
        errorTone();
        delay(2000);

        digitalWrite(RED_LED, LOW);
        lcd.clear();
        lcd.print("Ready");
        return;
      }

      if (response != "UNKNOWN") {

        digitalWrite(GREEN_LED, HIGH);

        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print("Welcome");

        lcd.setCursor(0,1);
        lcd.print(response);

        successTone();

        delay(3000);

        digitalWrite(GREEN_LED, LOW);
      }
      else {

        digitalWrite(RED_LED, HIGH);

        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print("Access Denied");

        lcd.setCursor(0,1);
        lcd.print("Not Registered");

        errorTone();

        delay(3000);

        digitalWrite(RED_LED, LOW);
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

  client.get("/image-endpoint");

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