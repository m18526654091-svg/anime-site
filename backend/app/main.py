from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import anime, comments, favorites, users
from .database import Base, engine, ensure_schema
from .seed import seed_anime

# Create tables (new DBs) + migrate existing DBs (add missing columns)
Base.metadata.create_all(bind=engine)
ensure_schema()
seed_anime()

app = FastAPI(title="AnimeHub API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(anime.router)
app.include_router(comments.router)
app.include_router(favorites.router)


@app.get("/")
def root():
    return {"service": "AnimeHub", "status": "running"}

