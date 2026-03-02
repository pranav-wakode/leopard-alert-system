from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import logging
import os
import time

from app.inference import LeopardDetector
from app.firebase import init_firebase, send_leopard_alert
from app.models import DetectionResponse, AlertResponse
from app.utils import draw_bounding_box

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Leopard Alert System")

# Strictly In-Memory State Constraints
state = {
    "alert_active": False,
    "last_detected_time": 0.0,
    "logs": [],
    "latest_image_b64": None,
    "total_detections": 0
}

# Template setup
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(templates_dir, exist_ok=True)
templates = Jinja2Templates(directory=templates_dir)

# Initialize detector
model_path = os.getenv("MODEL_PATH", "leopard-detection.onnx")
detector = LeopardDetector(model_path=model_path)

@app.on_event("startup")
async def startup_event():
    init_firebase()

@app.post("/predict", response_model=DetectionResponse)
async def predict(file: UploadFile = File(...)):
    image_bytes = await file.read()
    
    # Run ONNX inference
    detected, confidence, box = detector.detect(image_bytes)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_time = time.time()
    
    if detected:
        state["latest_image_b64"] = draw_bounding_box(image_bytes, box, confidence)
        
        # Only send push notification if we are triggering a NEW alert
        # (prevents spamming Firebase every single frame for 5 seconds)
        if not state["alert_active"] or (current_time - state["last_detected_time"] >= 5.0):
            send_leopard_alert(confidence)
            
        state["alert_active"] = True
        state["last_detected_time"] = current_time
        state["total_detections"] += 1
        
    else:
        state["latest_image_b64"] = draw_bounding_box(image_bytes, None, 0.0)
        # Note: We NO LONGER set alert_active to False here.
        # It will naturally expire during the /alert check.
    
    # Memory Logging logic
    log_entry = {
        "timestamp": timestamp,
        "detected": detected,
        "confidence": confidence if detected else None
    }
    state["logs"].insert(0, log_entry)
    
    # Prune logs to max 100 entries to prevent memory leak
    if len(state["logs"]) > 100:
        state["logs"] = state["logs"][:100]
        
    return DetectionResponse(detected=detected, confidence=confidence if detected else None)

@app.get("/alert", response_model=AlertResponse)
async def check_alert():
    """Polled by ESP32. Evaluates the 5-second cooldown timer."""
    current_time = time.time()
    
    if state["alert_active"]:
        if current_time - state["last_detected_time"] < 5.0:
            # Still within the 5-second window
            return AlertResponse(alert=True)
        else:
            # Cooldown expired
            state["alert_active"] = False
            return AlertResponse(alert=False)
            
    return AlertResponse(alert=False)

@app.get("/logs")
async def get_logs():
    return JSONResponse(content={"logs": state["logs"], "total": state["total_detections"]})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    # Determine UI status based on the cooldown timer
    is_alerting = False
    if state["alert_active"] and (time.time() - state["last_detected_time"] < 5.0):
        is_alerting = True
        
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "latest_image": state["latest_image_b64"],
        "logs": state["logs"][:10],
        "total_detections": state["total_detections"],
        "is_alerting": is_alerting
    })