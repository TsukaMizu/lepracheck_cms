import io
import time
import logging

import numpy as np
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)

# Model di-load sekali saat modul pertama kali di-import (startup)
_model = None


def load_model():
    """Load model Keras dari file .h5. Dipanggil saat startup aplikasi."""
    global _model
    try:
        import tensorflow as tf
        _model = tf.keras.models.load_model("leprosy_detection_model.h5")
        logger.info("Model ML berhasil di-load.")
    except Exception as e:
        logger.error(f"Gagal me-load model ML: {e}")
        _model = None


def is_model_loaded() -> bool:
    return _model is not None


def preprocess(image_bytes: bytes) -> np.ndarray:
    """Ubah bytes gambar menjadi tensor input untuk model (1, 64, 64, 3)."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((64, 64))
    x = np.array(img).astype(np.float32) / 255.0
    x = np.expand_dims(x, axis=0)
    return x


def predict(image_bytes: bytes) -> dict:
    """
    Jalankan inferensi pada gambar dan kembalikan hasil prediksi.

    Returns:
        dict dengan key: label, confidence, raw_score, inferenceMs

    Raises:
        RuntimeError: jika model belum di-load
        ValueError: jika file bukan gambar yang valid
    """
    if _model is None:
        raise RuntimeError("Model ML belum berhasil di-load.")

    try:
        x = preprocess(image_bytes)
    except (UnidentifiedImageError, Exception) as e:
        raise ValueError(f"File bukan gambar yang valid: {e}") from e

    start_time = time.time()
    raw = float(_model.predict(x, verbose=0)[0][0])
    inference_ms = round((time.time() - start_time) * 1000, 2)

    # raw >= 0.5 => model mengeluarkan probabilitas "Not Leprosy"
    if raw >= 0.5:
        label = "Tidak Ada Indikasi"
        confidence = raw
    else:
        label = "Indikasi"
        confidence = 1.0 - raw

    return {
        "label": label,
        "confidence": round(confidence, 6),
        "raw_score": round(raw, 6),
        "inferenceMs": inference_ms,
    }
