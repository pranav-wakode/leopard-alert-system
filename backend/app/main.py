from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import logging
import os

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
    "logs": [],
    "latest_image_b64": None,
    "total_detections": 0
}

# Template setup
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(templates_dir, exist_ok=True)
templates = Jinja2Templates(directory=templates_dir)

# Initialize detector (Assuming onnx model is mapped to root or relative path)
model_path = os.getenv("MODEL_PATH", "../leopard-detection.onnx")
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
    
    # Generate visualization
    if detected:
        state["latest_image_b64"] = draw_bounding_box(image_bytes, box, confidence)
        state["alert_active"] = True
        state["total_detections"] += 1
        
        # Trigger push notification
        send_leopard_alert(confidence)
    else:
        # Update dashboard with the latest clear frame
        state["latest_image_b64"] = draw_bounding_box(image_bytes, None, 0.0)
    
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
    """Polled by ESP32. Returns true once if an alert is queued, then resets."""
    current_alert = state["alert_active"]
    if current_alert:
        state["alert_active"] = False # Reset flag after ESP32 reads it
    return AlertResponse(alert=current_alert)

@app.get("/logs")
async def get_logs():
    return JSONResponse(content={"logs": state["logs"], "total": state["total_detections"]})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "latest_image": state["latest_image_b64"],
        "logs": state["logs"][:10], # Keep UI light
        "total_detections": state["total_detections"]
    })