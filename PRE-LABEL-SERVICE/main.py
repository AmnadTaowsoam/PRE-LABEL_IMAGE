import os
import time
import logging
import uvicorn
import numpy as np
import cv2
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from dotenv import load_dotenv
from httpx import AsyncClient
import httpx
from image_processing import predict_image

# Ensure the log directory exists
log_dir_path = '/home/qiadmin/quality_project/CONRNINSPEC-LABEL-IMAGE/data'
os.makedirs(log_dir_path, exist_ok=True)

# Set up logging to file
log_file_path = os.path.join(log_dir_path, 'log_file.log')
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_file_path),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

load_dotenv('/home/qiadmin/quality_project/CONRNINSPEC-LABEL-IMAGE/.env')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def log_request_info(request: Request):
    logger.debug(f"Request headers: {request.headers}")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"Request URL: {request.url}")

async def process_image(image_data: bytes, source: str):
    start_time = time.time()
    
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    logger.debug(f"Image shape: {image.shape}")
    logger.debug(f"Image dtype: {image.dtype}")

    output_data = predict_image(image_data)
    
    end_time = time.time()
    logger.info(f"Image processing time for {source}: {end_time - start_time:.2f} seconds")
    
    return output_data

async def send_results_to_label_studio(task_id, results):
    label_studio_url = os.getenv("LABEL_STUDIO_URL", "http://label-studio:8080")
    api_key = os.getenv("LABEL_STUDIO_API_KEY")
    endpoint = f"{label_studio_url}/api/predictions/"

    headers = {
        'Authorization': f'Token {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        "model_version": "1.0",
        "result": [{
            "from_name": "label",
            "to_name": "image",
            "type": "rectanglelabels",
            "value": r["value"],
            "score": r["score"]
        } for r in results],
        "score": max([d["score"] for d in results]) if results else 0,
        "task": task_id,
        "project": 1
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(endpoint, headers=headers, json=data)
        if response.status_code == 201:
            logger.info(f"Successfully sent results to Label Studio for task {task_id}")
        else:
            logger.error(f"Failed to send results to Label Studio. Status code: {response.status_code}, response: {response.text}")
            logger.debug(f"Response content: {response.json()}")
            logger.debug(f"Data sent: {data}")

@app.get("/health", status_code=200)
async def health_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)

@app.post("/setup", status_code=200)
async def setup():
    return JSONResponse(content={"status": "setup completed"}, status_code=200)

@app.post("/predict", status_code=200)
async def upload_image(request: Request, background_tasks: BackgroundTasks = None):
    log_request_info(request)
    logger.info("Received request on /predict endpoint")

    try:
        request_data = await request.json()
        logger.debug(f"Request data: {request_data}")

        tasks = request_data.get('tasks', [])
        if not tasks:
            logger.error("No tasks found in the request.")
            raise HTTPException(status_code=422, detail="No tasks found in the request.")

        task = tasks[0]
        image_path = task['data']['image']
        task_id = task['id']
        logger.info(f"Received image path from Label Studio: {image_path}")

        # Construct the full URL for the image
        label_studio_url = os.getenv("LABEL_STUDIO_URL", "http://label-studio:8080")
        image_url = f"{label_studio_url}{image_path}"
        logger.info(f"Constructed image URL: {image_url}")

        async with AsyncClient() as client:
            headers = {
                'Authorization': f'Token {os.getenv("LABEL_STUDIO_API_KEY")}'
            }
            try:
                image_response = await client.get(image_url, headers=headers)
                logger.debug(f"Image response status code: {image_response.status_code}")
                logger.info(f"Downloaded image content type: {image_response.headers.get('content-type')}")
            except Exception as e:
                logger.error(f"Error downloading image: {e}")
                raise HTTPException(status_code=500, detail=f"Error downloading image: {str(e)}")

            if image_response.status_code != 200:
                logger.error(f"Failed to download image. Status code: {image_response.status_code}")
                raise HTTPException(status_code=422, detail="Failed to download image from URL")

            image_data = image_response.content
            logger.info(f"Downloaded image size: {len(image_data)} bytes")

        output_data = await process_image(image_data, "predict")
        if not output_data:
            logger.error("Prediction process failed. No output data.")
            raise HTTPException(status_code=500, detail="Prediction process failed")

        logger.info("Image processed successfully.")
        if background_tasks:
            background_tasks.add_task(logger.debug, f"Full output data: {output_data}")

        # ส่งผลลัพธ์กลับไปยัง Label Studio
        await send_results_to_label_studio(task_id, output_data)

        # Format predictions for Label Studio
        predictions = [
            {
                "result": [{
                    "from_name": "label",
                    "to_name": "image",
                    "type": "rectanglelabels",
                    "value": r["value"],
                    "score": r["score"]
                } for r in output_data],
                "score": max([d["score"] for d in output_data]) if output_data else 0,
                "model_version": "1.0"
            }
        ]

        return JSONResponse(content={"predictions": predictions}, status_code=200)
    except HTTPException as e:
        logger.error(f"HTTP error during image processing: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during image processing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during image processing: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting Uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PRE_LABEL_PORT", 7000)))
    logger.info("Uvicorn server started.")