import asyncio
import httpx
import redis
import json
import os
from app.services.gemini import review_code
from app.services.github import post_pr_comment
from app.database import AsyncSessionLocal
from app.models.repo import Repo
from app.models.review import PRReview
from sqlalchemy import select

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"))

QUEUE_NAME = "pr_review_jobs"

async def process_job(job: dict):
    review_id = job["review_id"]
    diff_url = job["diff_url"]
    repo_name = job["repo_name"]
    pr_number = job["pr_number"]
    github_token = os.getenv("GITHUB_TOKEN", "")

    async with AsyncSessionLocal() as db:
        try:
            # 1. Fetch the actual diff from GitHub
            headers = {"Accept": "application/vnd.github.v3.diff"}
            if github_token:
                headers["Authorization"] = f"token {github_token}"

            async with httpx.AsyncClient() as client:
                response = await client.get(diff_url, headers=headers, follow_redirects=True)
                diff_content = response.text

            # 2. Send diff to Gemini
            print(f"🔍 Reviewing PR #{pr_number} in {repo_name}...")
            ai_review = await review_code(diff_content)

            # 3. Post comment back to GitHub PR
            await post_pr_comment(repo_name, pr_number, ai_review)
            print(f"💬 Comment posted to PR #{pr_number}")

            # 4. Update review record in DB
            result = await db.execute(select(PRReview).where(PRReview.id == review_id))
            review = result.scalar_one_or_none()

            if review:
                review.diff = diff_content
                review.ai_review = ai_review
                review.status = "completed"
                await db.commit()

            print(f"✅ Review {review_id} completed")

        except Exception as e:
            print(f"❌ Review {review_id} failed: {e}")
            result = await db.execute(select(PRReview).where(PRReview.id == review_id))
            review = result.scalar_one_or_none()
            if review:
                review.status = "failed"
                await db.commit()

async def run_worker():
    print("🚀 Worker started, waiting for jobs...")
    while True:
        job_data = redis_client.blpop(QUEUE_NAME, timeout=5)
        if job_data:
            _, raw = job_data
            job = json.loads(raw)
            print(f"📥 Got job: {job}")
            await process_job(job)
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(run_worker())