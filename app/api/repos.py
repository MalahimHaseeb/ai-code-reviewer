from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.repo import Repo
from pydantic import BaseModel

router = APIRouter()

class RepoRegisterRequest(BaseModel):
    github_repo_name: str 
    github_webhook_secret: str

class RepoResponse(BaseModel):
    id: int
    github_repo_name: str

    model_config = {"from_attributes": True}

@router.post("/repos/register", response_model=RepoResponse)
async def register_repo(payload: RepoRegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if already registered
    result = await db.execute(
        select(Repo).where(Repo.github_repo_name == payload.github_repo_name)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Repo already registered")

    repo = Repo(
        github_repo_name=payload.github_repo_name,
        github_webhook_secret=payload.github_webhook_secret
    )
    db.add(repo)
    await db.commit()
    await db.refresh(repo)

    return repo

@router.get("/repos", response_model=list[RepoResponse])
async def list_repos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Repo))
    repos = result.scalars().all()
    return repos