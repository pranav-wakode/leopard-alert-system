# Detailed Setup Guide

## 1. Google Cloud Setup
1. Go to Google Cloud Console and create a new project.
2. Enable **Cloud Run API** and **Artifact Registry API**.
3. Install the Google Cloud CLI (`gcloud`) on your local machine.
4. Authenticate:
```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
```

## 2. Firebase Setup
1. Go to Firebase Console and link to your Google Cloud project.
2. Go to **Project Settings > Service Accounts**.
3. Generate a new private key (Downloads a `.json` file).
4. Save this file locally (e.g., `firebase-credentials.json`). Do NOT commit this to GitHub.
5. In Cloud Run, you will mount this JSON as a secret and map it to the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.

## 3. Deployment to Cloud Run
From the `backend` directory containing the Dockerfile:
```bash
# Build the image and deploy in one step
gcloud run deploy leopard-alert-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --set-env-vars GOOGLE_APPLICATION_CREDENTIALS=/path/to/mounted/secret.json
```
(Note: Refer to GCP documentation on how to securely mount secrets in Cloud Run).

## 4. ESP32 Setup
1. Open Arduino IDE.
2. Install the **ESP32** board package via Boards Manager.
3. Install **ArduinoJson** by Benoit Blanchon via Library Manager.
4. Connect a Buzzer:
- Positive pin -> GPIO 12
- Negative pin -> GND
5. Open `esp32/esp32_alert.ino`, fill in your WiFi credentials and the Cloud Run URL.
6. Compile and upload to the ESP32-WROOM-32.

## 5. Phone / IP Camera Setup
1. Install **IP Webcam** from the Google Play Store on your spare Android phone.
2. Set video resolution to **640x480** or **640x640**.
3. Start the server. Note the IP address (e.g., `http://192.168.1.100:8080`).
4. To continuously send frames to the cloud, use a simple script or `curl` on a loop:
```bash
while true; do
  curl -s [http://192.168.1.100:8080/photo.jpg](http://192.168.1.100:8080/photo.jpg) > temp.jpg
  curl -X POST -F "file=@temp.jpg" https://YOUR_CLOUD_RUN_URL/predict
  sleep 1
done
```