from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

# Menggunakan SQLite agar sangat mudah dijalankan di laptop saat demo skripsi
SQLALCHEMY_DATABASE_URL = "sqlite:///./cms.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    category = Column(String, index=True)  # Kategori: Gejala, Pengobatan, Mitos, FAQ
    image_url = Column(String)
    read_time = Column(String)  # cth: '5 menit baca'
    is_featured = Column(Boolean, default=False)  # Untuk banner utama


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    video_url = Column(String)
    thumbnail_url = Column(String)
    duration = Column(String)  # cth: '04:15'


# Membuat tabel di database
Base.metadata.create_all(bind=engine)
