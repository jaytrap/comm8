from fastapi import FastAPI
from controllers.transcribe_controller import router as transcribe_router

app = FastAPI()

app.include_router(transcribe_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}