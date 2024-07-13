from fastapi import FastAPI, Request
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', 7001))

@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    # คุณสามารถตรวจสอบข้อมูลที่ได้รับและทำการกรองตามที่ต้องการได้ที่นี่
    subprocess.run(["python", "update_tasks.py"])
    return {"message": "Webhook received"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=WEBHOOK_PORT)

