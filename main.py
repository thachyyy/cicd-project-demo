from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.articles import router as articles_router
from schemas.models import HealthStatus

app = FastAPI(
    title="CI Demo API",
    description="A small CRUD service for managing articles.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles_router, prefix="/articles")


@app.get("/", response_model=HealthStatus)
async def health_check():
    return HealthStatus(status="healthy")
