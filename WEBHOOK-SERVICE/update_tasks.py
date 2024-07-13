import requests
import os
import logging

# Logging setup
logging.basicConfig(level=logging.DEBUG)

LABEL_STUDIO_API_KEY = os.getenv('LABEL_STUDIO_API_KEY')
LABEL_STUDIO_URL = os.getenv('LABEL_STUDIO_URL')
PROJECT_ID = os.getenv('PROJECT_ID')

def get_tasks():
    url = f"{LABEL_STUDIO_URL}/api/projects/{PROJECT_ID}/tasks"
    headers = {
        'Authorization': f'Token {LABEL_STUDIO_API_KEY}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def update_task(task_id, data):
    url = f"{LABEL_STUDIO_URL}/api/tasks/{task_id}"
    headers = {
        'Authorization': f'Token {LABEL_STUDIO_API_KEY}',
        'Content-Type': 'application/json'
    }
    response = requests.patch(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def main():
    tasks = get_tasks()
    logging.debug(f"Fetched tasks: {tasks}")

    for task in tasks:
        task_id = task['id']
        logging.debug(f"Updating task {task_id} with data: {data}")
        try:
            update_response = update_task(task_id, {
                "predictions": [
                    {
                        "result": [
                            {
                                "value": {
                                    "choices": ["Choice"]
                                },
                                "from_name": "choices",
                                "to_name": "image"
                            }
                        ],
                        "score": 0.5,
                        "model_version": "1.0",
                        "created_ago": "0 min ago",
                        "created_by": 1,
                        "cluster": 0
                    }
                ]
            })
            logging.debug(f"Task {task_id} updated successfully: {update_response}")
        except requests.RequestException as e:
            logging.error(f"Failed to update task {task_id}: {e}")

if __name__ == "__main__":
    main()
