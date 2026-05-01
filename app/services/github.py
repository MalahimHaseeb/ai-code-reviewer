import hmac
import hashlib
import httpx
import os

def verify_signature(payload: bytes, signature: str) -> bool:
    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "").encode()
    expected = "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

def extract_pr_data(payload: dict) -> dict | None:
    action = payload.get("action")

    if action not in ["opened", "synchronize"]:
        return None

    pr = payload.get("pull_request", {})
    repo = payload.get("repository", {})

    return {
        "repo_name": repo.get("full_name"),
        "pr_number": pr.get("number"),
        "pr_title": pr.get("title"),
        "diff_url": pr.get("diff_url"),
        "head_sha": pr.get("head", {}).get("sha"),
    }

async def post_pr_comment(repo_name: str, pr_number: int, comment: str):
    token = os.getenv("GITHUB_TOKEN", "")
    url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    body = {"body": f"## 🤖 AI Code Review\n\n{comment}"}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=body, headers=headers)
        response.raise_for_status()
        return response.json()