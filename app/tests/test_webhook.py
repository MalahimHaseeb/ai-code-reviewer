import pytest
import hmac
import hashlib
import json
from unittest.mock import patch, AsyncMock

def make_signature(payload: dict, secret: str) -> str:
    body = json.dumps(payload).encode()
    sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={sig}"

WEBHOOK_SECRET = "malahim_super_secret_2026"

SAMPLE_PR_PAYLOAD = {
    "action": "opened",
    "pull_request": {
        "number": 42,
        "title": "Add new feature",
        "diff_url": "https://github.com/malahim/test-repo/pull/42.diff",
        "head": {"sha": "abc123"}
    },
    "repository": {
        "full_name": "malahim/test-repo"
    }
}

@pytest.mark.asyncio
async def test_webhook_invalid_signature(client):
    response = await client.post(
        "/api/webhook",
        json=SAMPLE_PR_PAYLOAD,
        headers={"X-Hub-Signature-256": "sha256=invalidsignature"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_webhook_repo_not_registered(client):
    payload_bytes = json.dumps(SAMPLE_PR_PAYLOAD).encode()
    signature = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(), payload_bytes, hashlib.sha256
    ).hexdigest()

    with patch("app.api.webhook.verify_signature", return_value=True):
        response = await client.post(
            "/api/webhook",
            content=payload_bytes,
            headers={
                "X-Hub-Signature-256": signature,
                "Content-Type": "application/json"
            }
        )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_webhook_success(client):
    # Register repo first
    await client.post("/api/repos/register", json={
        "github_repo_name": "malahim/test-repo",
        "github_webhook_secret": WEBHOOK_SECRET
    })

    payload_bytes = json.dumps(SAMPLE_PR_PAYLOAD).encode()

    with patch("app.api.webhook.verify_signature", return_value=True), \
         patch("app.api.webhook.redis_client") as mock_redis:

        response = await client.post(
            "/api/webhook",
            content=payload_bytes,
            headers={
                "X-Hub-Signature-256": "sha256=test",
                "Content-Type": "application/json"
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert "review_id" in data

@pytest.mark.asyncio
async def test_webhook_ignores_non_pr_events(client):
    payload = {**SAMPLE_PR_PAYLOAD, "action": "closed"}
    payload_bytes = json.dumps(payload).encode()

    with patch("app.api.webhook.verify_signature", return_value=True):
        response = await client.post(
            "/api/webhook",
            content=payload_bytes,
            headers={
                "X-Hub-Signature-256": "sha256=test",
                "Content-Type": "application/json"
            }
        )
    assert response.status_code == 200
    assert response.json()["status"] == "ignored"