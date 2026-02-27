import cv2
import base64
import numpy as np

def draw_bounding_box(image_bytes, box, confidence):
    """
    Decodes the image, draws the bounding box if detected, 
    and returns a base64 encoded string.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if box and img is not None:
        x1, y1, x2, y2 = [int(v) for v in box]
        # Draw red rectangle
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        # Draw label
        label = f"Leopard: {confidence * 100:.1f}%"
        cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
    # Encode back to jpeg in memory
    _, buffer = cv2.imencode('.jpg', img)
    # Return base64 string for HTML rendering
    return base64.b64encode(buffer).decode('utf-8')