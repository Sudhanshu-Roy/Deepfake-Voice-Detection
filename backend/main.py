import logging
import os
import tempfile

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from origin_guard import load_allowed_origins, origin_is_allowed
from src.predict import WEIGHTS_PATH, predict_audio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deepfake")

MAX_BYTES = 25 * 1024 * 1024
OPEN_PATHS = {"/", "/health"}
ALLOWED_ORIGINS = load_allowed_origins()

app = FastAPI(title="Deepfake Voice Detector")


@app.middleware("http")
async def allow_frontend_only(request: Request, call_next):
    if request.url.path in OPEN_PATHS:
        return await call_next(request)

    if not origin_is_allowed(request.headers.get("origin"), ALLOWED_ORIGINS):
        return JSONResponse(
            status_code=403,
            content={"detail": "This API only accepts requests from the deployed frontend."},
        )

    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=list(ALLOWED_ORIGINS),
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

logger.info("Model weights: %s", WEIGHTS_PATH)


@app.get("/")
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    filename = file.filename or ""
    if not filename.lower().endswith(".wav"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a WAV file.",
        )

    data = await file.read()
    if not data:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )
    if len(data) > MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File is too large. Maximum size is 25 MB.",
        )
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        raise HTTPException(
            status_code=400,
            detail="Please upload a WAV file.",
        )

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav",
        ) as tmp_file:
            tmp_file.write(data)
            temp_path = tmp_file.name

        prediction, confidence = predict_audio(temp_path)
        confidence = float(confidence)
        if confidence != confidence:
            raise HTTPException(
                status_code=400,
                detail="Audio must be at least 1 second long.",
            )

        return {
            "prediction": prediction,
            "confidence": confidence,
        }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Prediction failed")
        raise HTTPException(
            status_code=400,
            detail="Could not score that file. Use a WAV clip at least 1 second long.",
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
