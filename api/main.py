from fastapi import FastAPI
import time

app = FastAPI()

@app.get("/api/v1/ping")
async def ping():
    return {"status": "pong", "timestamp": time.time()}
