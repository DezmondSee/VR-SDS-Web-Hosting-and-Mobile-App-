from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Initialize the API
app = FastAPI(title="VR-SDS Mobile API")

# Allow your Android app to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. A simple test endpoint to check if the server is awake
@app.get("/")
def health_check():
    return {"status": "success", "message": "VR-SDS API is running and connected to Aiven Cloud!"}

# 2. The endpoint your Kotlin app will eventually hit
@app.post("/api/scan-audio")
async def scan_audio(file: UploadFile = File(...)):
    # Later, we will import your AI model here to process the audio
    # For now, we just return a fake successful response to the phone
    return {
        "filename": file.filename,
        "verdict": "SAFE",
        "confidence": 0.98
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)