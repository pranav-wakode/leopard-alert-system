import os
import json
import firebase_admin
from firebase_admin import credentials, messaging
import logging

logger = logging.getLogger(__name__)

def init_firebase():
    try:
        # Check if already initialized to prevent errors on reloads
        firebase_admin.get_app()
    except ValueError:
        try:
            secret_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            if secret_json:
                try:
                    # Attempt to parse as JSON string (Cloud Run secret injection)
                    cred_dict = json.loads(secret_json)
                    cred = credentials.Certificate(cred_dict)
                except json.JSONDecodeError:
                    # Fallback to file path if it's not valid JSON (Local testing)
                    cred = credentials.Certificate(secret_json)
                    
                firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized successfully.")
            else:
                logger.warning("GOOGLE_APPLICATION_CREDENTIALS not set. Push notifications will be disabled.")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")

def send_leopard_alert(confidence: float):
    """
    Sends a push notification to all subscribed devices using a Firebase topic.
    """
    try:
        # Check if Firebase is initialized
        firebase_admin.get_app()
        
        message = messaging.Message(
            notification=messaging.Notification(
                title="Leopard Detected!",
                body=f"Confidence: {confidence * 100:.1f}%",
            ),
            topic="leopard_alerts", # Devices must subscribe to this topic
        )
        
        response = messaging.send(message)
        logger.info(f"Successfully sent Firebase message: {response}")
        return True
    except ValueError:
        logger.warning("Firebase not initialized. Cannot send alert.")
        return False
    except Exception as e:
        logger.error(f"Error sending Firebase message: {e}")
        return False