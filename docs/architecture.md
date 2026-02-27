# System Architecture

## Overview
The Leopard Detection Alert System is an edge-to-cloud IoT solution. It utilizes an old smartphone as an IP Camera to capture continuous frames, processes them in a scalable cloud environment using YOLOv8, and alerts users via both software (Push Notifications) and hardware (ESP32 Buzzer).

## Components
1. **IP Camera (Phone)**
   - Acts as the image source.
   - Pushes JPEG snapshots to the `/predict` endpoint via standard HTTP POST.

2. **Cloud Backend (FastAPI + ONNX)**
   - Hosted on Google Cloud Run.
   - Stateless operation (in-memory only).
   - Runs `leopard-detection.onnx` using `onnxruntime`.
   - Generates Base64 encoded bounding-box visualizations.
   - Acts as the central orchestrator.

3. **Firebase Cloud Messaging (FCM)**
   - Triggered by the backend if confidence > 50%.
   - Broadcasts push notifications to the `leopard_alerts` topic.

4. **Hardware Alarms (ESP32)**
   - A dedicated ESP32 microcontroller polling the `/alert` API endpoint.
   - Once the endpoint flags `alert: true`, the ESP32 activates a high-decibel buzzer for 5 seconds.