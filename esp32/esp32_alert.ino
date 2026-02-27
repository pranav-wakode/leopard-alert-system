#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h> // Requires ArduinoJson library by Benoit Blanchon

// --- Configuration ---
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "https://YOUR_CLOUD_RUN_URL/alert"; // Replace with actual backend URL

const int BUZZER_PIN = 12; // GPIO pin connected to the buzzer

void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("
Connected to WiFi!");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    int httpResponseCode = http.GET();

    if (httpResponseCode == 200) {
      String payload = http.getString();
      
      // Parse JSON response: {"alert": true/false}
      StaticJsonDocument<200> doc;
      DeserializationError error = deserializeJson(doc, payload);

      if (!error) {
        bool alert = doc["alert"];
        if (alert) {
          Serial.println("ALERT! Leopard detected! Activating buzzer...");
          digitalWrite(BUZZER_PIN, HIGH);
          delay(5000); // Sound buzzer for 5 seconds
          digitalWrite(BUZZER_PIN, LOW);
        } else {
          Serial.println("Status: Clear");
        }
      } else {
        Serial.print("JSON parsing failed: ");
        Serial.println(error.c_str());
      }
    } else {
      Serial.print("HTTP Error code: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("WiFi Disconnected. Reconnecting...");
    WiFi.reconnect();
  }

  delay(2000); // Poll /alert endpoint every 2 seconds
}