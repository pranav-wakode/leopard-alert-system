import cv2
import numpy as np
import onnxruntime as ort
import logging

logger = logging.getLogger(__name__)

class LeopardDetector:
    def __init__(self, model_path="leopard-detection.onnx"):
        self.model_path = model_path
        self.session = None
        self.input_name = None
        self.load_model()

    def load_model(self):
        try:
            # Attempt to use GPU (CUDA), fallback to CPU
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
            self.session = ort.InferenceSession(self.model_path, providers=providers)
            self.input_name = self.session.get_inputs()[0].name
            logger.info(f"Model loaded successfully from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load ONNX model: {e}")

    def preprocess(self, image_bytes):
        # Decode image from memory
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        original_h, original_w = img.shape[:2]
        
        # YOLOv8 standard preprocessing: 640x640, RGB, normalize 0-1, NCHW
        img_resized = cv2.resize(img, (640, 640))
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        img_normalized = img_rgb / 255.0
        img_transposed = np.transpose(img_normalized, (2, 0, 1))
        img_expanded = np.expand_dims(img_transposed, axis=0).astype(np.float32)
        
        return img_expanded, original_w, original_h

    def detect(self, image_bytes, conf_threshold=0.5):
        if not self.session:
            logger.error("Inference session not initialized.")
            return False, 0.0, None

        try:
            input_tensor, orig_w, orig_h = self.preprocess(image_bytes)
            outputs = self.session.run(None, {self.input_name: input_tensor})
            
            # Simplified YOLOv8 parsing (assuming single class: leopard)
            predictions = outputs[0][0] # shape e.g. (5, 8400)
            predictions = np.transpose(predictions) # shape (8400, 5)
            
            best_conf = 0.0
            best_box = None
            
            for pred in predictions:
                conf = pred[4] # Confidence score
                if conf > conf_threshold and conf > best_conf:
                    best_conf = float(conf)
                    # Convert center x, center y, w, h to x1, y1, x2, y2
                    xc, yc, w, h = pred[0], pred[1], pred[2], pred[3]
                    # Scale coordinates back to original image size
                    x1 = (xc - w/2) * (orig_w / 640.0)
                    y1 = (yc - h/2) * (orig_h / 640.0)
                    x2 = (xc + w/2) * (orig_w / 640.0)
                    y2 = (yc + h/2) * (orig_h / 640.0)
                    best_box = [x1, y1, x2, y2]
                    
            if best_conf > conf_threshold:
                return True, best_conf, best_box
            return False, 0.0, None
            
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return False, 0.0, None