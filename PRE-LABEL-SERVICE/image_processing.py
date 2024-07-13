import logging
import numpy as np
import cv2
from ultralytics import YOLO

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the paths for the YOLO models directly
DET_MODEL_PATH = './best_model/detection/best.pt'
CLS_MODEL_PATH = './best_model/classify/best.pt'

# Load YOLO models once at the start
try:
    det_model = YOLO(DET_MODEL_PATH)
    cls_model = YOLO(CLS_MODEL_PATH)
    logger.info("YOLO models loaded successfully")
except Exception as e:
    logger.error(f"Error loading YOLO models: {e}")
    raise

def predict_image(image_data):
    """
    Predict image using YOLO model for detection and classification.
    Parameters:
    - image_data: bytes, image data to be processed
    Returns:
    - output_data: list, containing detected objects with classifications
    """
    try:
        # Image decoding
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Failed to decode image")
        logger.info(f"Image decoded successfully. Shape: {image.shape}, dtype: {image.dtype}")

        # Object detection
        results = det_model.predict(image, verbose=False, conf=0.5, max_det=1000)
        logger.debug(f"Detection results: {results}")

        output_data = []
        boxes = results[0].boxes.data.cpu().numpy()
        seed_count = len(boxes)
        logger.info(f"Seed count: {seed_count}")

        if seed_count == 0:
            logger.info("No seeds detected")
            return []

        image_height, image_width = image.shape[:2]

        for i, box in enumerate(boxes):
            x1, y1, x2, y2, conf = map(float, box[:5])
            x1, y1, x2, y2, conf = int(x1), int(y1), int(x2), int(y2), float(conf)
            cropped_image = image[y1:y2, x1:x2]
            logger.debug(f"Processing bounding box {i+1}/{seed_count}: {(x1, y1, x2, y2)}")

            try:
                cls_result = cls_model.predict(cropped_image, save=False, conf=0.90)
                if cls_result:
                    result = cls_result[0]
                    max_index = result.probs.top1
                    max_conf = result.probs.top1conf.item()
                    max_conf_class = result.names[max_index]

                    logger.debug(f"Box {i+1} classified as {max_conf_class} with confidence {max_conf}")
                    output_data.append({
                        "id": f"{x1}-{y1}-{x2}-{y2}",
                        "type": "rectanglelabels",
                        "value": {
                            "x": float(x1 / image_width * 100),  # Convert to percentage
                            "y": float(y1 / image_height * 100),  # Convert to percentage
                            "width": float((x2 - x1) / image_width * 100),  # Convert to percentage
                            "height": float((y2 - y1) / image_height * 100),  # Convert to percentage
                            "rotation": 0,
                            "rectanglelabels": [max_conf_class]  # Use classified label
                        },
                        "score": float(max_conf)  # Ensure the score is a float
                    })

            except Exception as cls_e:
                logger.error(f"Error classifying box {i+1}: {cls_e}")

        logger.info(f"Image processed successfully. {len(output_data)} boxes detected.")
        return output_data

    except Exception as e:
        logger.error(f"Error in predict_image: {e}")
        raise
