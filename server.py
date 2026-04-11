from fastapi import FastAPI, File, UploadFile
from PIL import Image
import numpy as np
import io
import tensorflow as tf

app = FastAPI(title="LepraCheck ML Service")

model = tf.keras.models.load_model("leprosy_detection_model.h5")

def preprocess(image_bytes: bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((64, 64))
    x = np.array(img).astype(np.float32) / 255.0
    x = np.expand_dims(x, axis=0)  # (1, 64, 64, 3)
    return x

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image_bytes = await file.read()
    x = preprocess(image_bytes)

    raw = float(model.predict(x)[0][0])

    # mapping untuk app Flutter kamu:
    # repo: raw >= 0.5 => Not Leprosy
    if raw >= 0.5:
        label = "tidak_indikasi"
        confidence = raw
    else:
        label = "indikasi"
        confidence = 1.0 - raw

    return {"label": label, "confidence": confidence, "raw_score": raw}