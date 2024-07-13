# Dockerfile.update-task
FROM python:3.10-slim

WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY update_tasks.py .

# Add a wait-for-it.sh script if it is not already included
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Command to run the service
CMD ["/wait-for-it.sh", "label-studio:8080", "--", "python", "update_tasks.py"]
