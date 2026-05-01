import pytest

@pytest.mark.asyncio
async def test_register_repo(client):
    response = await client.post("/api/repos/register", json={
        "github_repo_name": "malahim/test-repo",
        "github_webhook_secret": "supersecret"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["github_repo_name"] == "malahim/test-repo"
    assert "id" in data

@pytest.mark.asyncio
async def test_register_duplicate_repo(client):
    # Register once
    await client.post("/api/repos/register", json={
        "github_repo_name": "malahim/test-repo",
        "github_webhook_secret": "supersecret"
    })
    # Register again — should fail
    response = await client.post("/api/repos/register", json={
        "github_repo_name": "malahim/test-repo",
        "github_webhook_secret": "supersecret"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Repo already registered"

@pytest.mark.asyncio
async def test_list_repos_empty(client):
    response = await client.get("/api/repos")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_list_repos(client):
    await client.post("/api/repos/register", json={
        "github_repo_name": "malahim/test-repo",
        "github_webhook_secret": "supersecret"
    })
    response = await client.get("/api/repos")
    assert response.status_code == 200
    assert len(response.json()) == 1