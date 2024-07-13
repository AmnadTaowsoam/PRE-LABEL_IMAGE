import os
import logging
import requests
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

LABEL_STUDIO_API_KEY = os.getenv("LABEL_STUDIO_API_KEY")
LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL")
PROJECT_ID = os.getenv("PROJECT_ID")
ML_BACKEND_URL = os.getenv("ML_BACKEND_URL")

def update_tasks():
    try:
        logger.debug("Starting update_tasks process")

        if not all([LABEL_STUDIO_API_KEY, LABEL_STUDIO_URL, PROJECT_ID, ML_BACKEND_URL]):
            logger.error("One or more environment variables are missing")
            logger.debug(f"LABEL_STUDIO_API_KEY: {LABEL_STUDIO_API_KEY}")
            logger.debug(f"LABEL_STUDIO_URL: {LABEL_STUDIO_URL}")
            logger.debug(f"PROJECT_ID: {PROJECT_ID}")
            logger.debug(f"ML_BACKEND_URL: {ML_BACKEND_URL}")
            return

        headers = {
            'Authorization': f'Token {LABEL_STUDIO_API_KEY}',
        }

        logger.debug(f"Fetching tasks from {LABEL_STUDIO_URL}/api/projects/{PROJECT_ID}/tasks")
        response = requests.get(f"{LABEL_STUDIO_URL}/api/projects/{PROJECT_ID}/tasks", headers=headers)
        response.raise_for_status()
        tasks = response.json()

        logger.debug(f"Fetched tasks: {tasks}")

        for task in tasks:
            task_id = task['id']
            data = {
                "predictions": [
                    {
                        "result": [{"value": {"choices": ["Choice"]}, "from_name": "choices", "to_name": "image"}],
                        "score": 0.5,
                        "model_version": "1.0",
                        "created_ago": "0 min ago",
                        "created_by": 1,
                        "cluster": 0
                    }
                ]
            }

            logger.debug(f"Updating task {task_id} with data: {data}")
            response = requests.post(f"{ML_BACKEND_URL}/api/predictions/{task_id}", json=data, headers=headers)
            response.raise_for_status()
            logger.debug(f"Updated task {task_id} with response: {response.json()}")

    except requests.exceptions.RequestException as e:
        logger.error(f"RequestException occurred: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    logger.debug("Starting the update-task-service script")
    while True:
        update_tasks()
        logger.debug("Sleeping for 10 minutes before the next update")
        time.sleep(600)  # Sleep for 10 minutes before the next update
