from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import init_db
from app.models import repo, review
from app.api.webhook import router as webhook_router
from app.api.repos import router as repos_router
from app.api.dummy import router as dummy_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="AI Code Reviewer",
    description="Automated AI-powered GitHub PR reviews",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(webhook_router, prefix="/api")
app.include_router(repos_router, prefix="/api")
app.include_router(dummy_router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI Code Reviewer is running"}