#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "Oppo Oppo";
const char* password = "Hi There";

const char* host = "leopard-alert-backend-xxxxx-uc.a.run.app"; // Replace with your Cloud Run URL
const char* url = "/alert";

const int BUZZER_PIN = 12;

WiFiClientSecure client;

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

  Serial.println("\nConnected to WiFi!");
  client.setInsecure();  // Skip certificate validation
}

void loop() {

  if (WiFi.status() == WL_CONNECTED) {

    WiFiClientSecure client;
    client.setInsecure();

    HTTPClient https;

    String fullUrl = String("https://") + host + url;

    Serial.println("Requesting: " + fullUrl);

    https.begin(client, fullUrl);

    int httpCode = https.GET();

    if (httpCode > 0) {

      String payload = https.getString();

      Serial.println("Response:");
      Serial.println(payload);

      StaticJsonDocument<200> doc;
      DeserializationError error = deserializeJson(doc, payload);

      if (!error) {

        bool alert = doc["alert"];

        if (alert) {
          Serial.println("ALERT! Activating buzzer...");
          digitalWrite(BUZZER_PIN, HIGH);
          delay(5000);
          digitalWrite(BUZZER_PIN, LOW);
        } else {
          Serial.println("Status: Clear");
        }

      } else {
        Serial.println("JSON parse failed.");
      }

    } else {
      Serial.print("HTTP error: ");
      Serial.println(httpCode);
    }

    https.end();
  }

  delay(3000);
}