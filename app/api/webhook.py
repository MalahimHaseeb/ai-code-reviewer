from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.repo import Repo
from app.models.review import PRReview
from app.services.github import verify_signature, extract_pr_data
import redis
import json
import os

router = APIRouter()

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"))

QUEUE_NAME = "pr_review_jobs"

@router.post("/webhook")
async def github_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload_bytes = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not verify_signature(payload_bytes, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    pr_data = extract_pr_data(payload)

    if not pr_data:
        return {"status": "ignored", "reason": "not a PR open/sync event"}

    result = await db.execute(
        select(Repo).where(Repo.github_repo_name == pr_data["repo_name"])
    )
    repo = result.scalar_one_or_none()

    if not repo:
        raise HTTPException(status_code=404, detail="Repo not registered")

    # Save review as pending
    review = PRReview(
        repo_id=repo.id,
        pr_number=pr_data["pr_number"],
        pr_title=pr_data["pr_title"],
        diff=pr_data["diff_url"],
        status="pending"
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)

    # Push job to Redis queue
    job = {
        "review_id": review.id,
        "diff_url": pr_data["diff_url"],
        "repo_name": pr_data["repo_name"],
        "pr_number": pr_data["pr_number"],
    }
    redis_client.rpush(QUEUE_NAME, json.dumps(job))

    return {"status": "queued", "review_id": review.id}