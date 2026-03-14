# 🛠 Setup Guide

This guide explains how to deploy and run the **Leopard Detection Alert System** from scratch.

The system consists of:
- Cloud backend (AI inference)
- Firebase notifications
- Android camera app
- ESP32 hardware alert

## 1️⃣ Prerequisites

You must install:

### Required Software
- Python 3.10+
- Docker (optional but recommended)
- Arduino IDE
- Google Cloud CLI (gcloud)

### Hardware
- ESP32 DevKit V1
- Active buzzer module
- Android phone

## 2️⃣ Clone Repository
```bash
git clone https://github.com/pranav-wakode/leopard-alert-system
cd leopard-alert-system
```

### 3️⃣ Google Cloud Setup

We deploy the backend using **Google Cloud Run**.

### Step 1 — Create Google Cloud Project

Open:

https://console.cloud.google.com/

Create a new project.

Example:
```
leopard-alert-system
```

### Step 2 — Enable Required APIs

Enable these APIs:
```
Cloud Run API
Cloud Build API
Artifact Registry API
Secret Manager API
```

### Step 3 — Install Google Cloud CLI

Ubuntu example:
```bash
sudo apt install google-cloud-cli
```

### Step 4 — Login to Google Cloud
```bash
gcloud auth login
```

### Step 5 — Select Project
```bash
gcloud config set project YOUR_PROJECT_ID
```

Example:
```bash
gcloud config set project leopard-alert-system
```

## 4️⃣ Firebase Setup

⚠️ **Important**:
Use the **same Google Cloud project** when creating Firebase.

This avoids authentication and service account issues.

### Step 1 — Create Firebase Project

Open:

https://console.firebase.google.com

Click:
```
Add project
```

Choose:
```
Import existing Google Cloud project
```

Select:
```
leopard-alert-system
```

### Step 2 — Enable Cloud Messaging

Go to:
```
Firebase Console → Cloud Messaging
```

No extra configuration required.

### Step 3 — Generate Service Account Key

Navigate:
```
Firebase → Project Settings
→ Service Accounts
```

Click:
```
Generate new private key
```

Download the JSON file.

Example:
```
firebase-credentials.json
```

## 5️⃣ Store Firebase Secret in Cloud

Upload the JSON key to Google Secret Manager.
```bash
gcloud secrets create firebase-credentials \
  --data-file=firebase-credentials.json
```

Grant Cloud Run permission:
```bash
gcloud secrets add-iam-policy-binding firebase-credentials \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## 6️⃣ Backend Setup

Navigate to backend folder:
```bash
cd backend
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Add Model

Place the ONNX model inside:
```
backend/
```

Example:
```
backend/leopard-detection.onnx
```

### Run Locally
```bash
uvicorn app.main:app --reload --port 8080
```

Open dashboard:
```
http://localhost:8080/dashboard
or
https://leopard-alert-backend-xxxxx-uc.a.run.app/dashboard
```


## 7️⃣ Deploy Backend to Cloud Run

Deploy using:
```bash
gcloud run deploy leopard-alert-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --set-secrets GOOGLE_APPLICATION_CREDENTIALS=firebase-credentials:latest
```

After deployment you will receive a service URL:
```
https://leopard-alert-backend-xxxxx-uc.a.run.app
```

Use this URL for:
- Android app
- ESP32 device

## 8️⃣ Android App Setup

Android app responsibilities:
- capture camera frames
- upload images to backend
- receive push notifications

Android app source code is available here:

[https://github.com/pranav-wakode/leopard-android](https://github.com/pranav-wakode/leopard-android)

### Step 1 — Add Firebase to Android

Go to Firebase Console:
```
Project Settings → Add Android App
```

Enter package name of Android app.

Download:
```
google-services.json
```

Place inside:
```
app/google-services.json
```

### Step 2 — Subscribe to Alert Topic

The app subscribes to topic:
```
leopard_alerts
```

Example code:
```
FirebaseMessaging.getInstance().subscribeToTopic("leopard_alerts")
```

### Step 3 — Configure Backend URL

Update API endpoint in Android app:
```
https://YOUR_CLOUD_RUN_URL/predict
```

## 9️⃣ ESP32 Setup

ESP32 polls backend `/alert` endpoint.

### Hardware Wiring

Connect buzzer module:
```
ESP32 GPIO12 → Buzzer Signal
ESP32 3.3V   → Buzzer VCC
ESP32 GND    → Buzzer GND
```

### Install ESP32 Board in Arduino IDE

Open:
```
File → Preferences
```

Add board URL:
```
https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
```

Install:
```
ESP32 by Espressif Systems
```

### Install Required Library

Install from Library Manager:
```
ArduinoJson
```

### Configure WiFi and Backend

Update variables in code:
```cpp
const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASSWORD";

const char* host = "YOUR_CLOUD_RUN_DOMAIN";
const char* url = "/alert";
```

Example:
```cpp
const char* host = "leopard-alert-backend-xxxxx-uc.a.run.app";
```

### Upload Code

Select board:
```
ESP32 Dev Module
```

Upload the sketch.

Open Serial Monitor:
```
115200 baud
```

Expected output:
```
Status: Clear
```

## 🔟 System Test
- Open Android app
- Start camera capture
- Show leopard image

Expected results:
```
AI detection triggered
Firebase notification sent
ESP32 buzzer activated
Dashboard updated
```

## 🚀 Final Result

This project demonstrates a **complete AI + Cloud + IoT pipeline**:
- Real-time wildlife detection
- Serverless cloud inference
- Mobile push alerts
- Hardware alarm system