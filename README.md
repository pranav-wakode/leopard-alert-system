# 🐆 Leopard Detection Alert System

A complete edge-to-cloud IoT alert system for detecting leopards. Built with FastAPI, YOLOv8 (ONNX), Firebase, and ESP32.

## Features
- **Real-time Inference:** YOLOv8 ONNX model running in memory.
- **Stateless & Ephemeral:** Zero permanent image storage; adheres to strict privacy and resource constraints.
- **Hardware Integration:** ESP32 polling mechanism to trigger physical alarms (buzzers).
- **Push Notifications:** Firebase integration for instant mobile alerts.
- **Web Dashboard:** Real-time visualization of the camera feed and detection logs.

## Project Structure
- `/backend`: FastAPI application, ONNX inference, and Docker setup.
- `/esp32`: Arduino code for the hardware alarm.
- `/docs`: Architecture diagrams and detailed setup guides.

## Quickstart (Local Testing)
1. Place your `leopard-detection.onnx` file in the root or backend directory.
2. Set up a virtual environment and install requirements:
```bash
   cd backend
   pip install -r requirements.txt
```
3. Run the server locally:
```bash
uvicorn app.main:app --reload --port 8080
```
4. Access the dashboard at `http://localhost:8080/dashboard`.
5. Post an image to test:
```bash
curl -X POST -F "file=@test_image.jpg" http://localhost:8080/predict
```
For full deployment to Google Cloud Run and hardware setup, see `docs/setup_guide.md`.