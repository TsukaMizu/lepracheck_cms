from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqladmin import Admin, ModelView

from database import engine, SessionLocal, Article, Video
import ml_service

# Ukuran maksimum file gambar yang diterima: 10 MB
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    ml_service.load_model()
    yield


app = FastAPI(title="LepraCheck CMS & ML API", lifespan=lifespan)

# Setup CORS agar Flutter bisa akses API ini (lokal atau network)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- KONFIGURASI SQLADMIN (Panel UI CMS) ---
admin = Admin(app, engine)


class ArticleAdmin(ModelView, model=Article):
    column_list = [Article.id, Article.title, Article.category, Article.is_featured]
    name = "Artikel Edukasi"
    name_plural = "Artikel Edukasi"
    icon = "fa-solid fa-newspaper"


class VideoAdmin(ModelView, model=Video):
    column_list = [Video.id, Video.title, Video.duration]
    name = "Video Edukasi"
    name_plural = "Video Edukasi"
    icon = "fa-solid fa-video"


admin.add_view(ArticleAdmin)
admin.add_view(VideoAdmin)
# -------------------------------------------


# Dependency untuk mendapatkan koneksi DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- ENDPOINT API UNTUK FLUTTER ---
@app.get("/api/articles")
def read_articles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    articles = db.query(Article).offset(skip).limit(limit).all()
    return articles


@app.get("/api/videos")
def read_videos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    videos = db.query(Video).offset(skip).limit(limit).all()
    return videos


@app.get("/")
def root():
    return {
        "message": "LepraCheck CMS API is running!",
        "admin_panel": "Buka /admin untuk mengelola konten",
    }


# --- ENDPOINT HEALTH CHECK ---
@app.get("/health")
def health():
    return {
        "status": "ok",
        "ml_model_loaded": ml_service.is_model_loaded(),
    }


# --- ENDPOINT ML DETEKSI LEPRA ---
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Tipe file tidak didukung: {file.content_type}. Gunakan JPEG, PNG, WebP, atau BMP.",
        )
    image_bytes = await file.read()
    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Ukuran file terlalu besar. Maksimal {MAX_IMAGE_SIZE_BYTES // (1024 * 1024)} MB.",
        )
    try:
        result = ml_service.predict(image_bytes)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return result
