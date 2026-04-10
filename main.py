from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqladmin import Admin, ModelView

from database import engine, SessionLocal, Article, Video

app = FastAPI(title="LepraCheck CMS API")

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
