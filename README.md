# AI Code Reviewer

A self-hostable API that automatically reviews GitHub Pull Requests using AI (Google Gemini).

When a PR is opened, GitHub sends a webhook to this service, which queues the job, fetches the diff, runs an AI review, and posts the feedback as a PR comment.

## Tech Stack

- FastAPI — Webhook receiver and REST API
- PostgreSQL — Stores repositories and review history
- Redis — Job queue for asynchronous processing
- Docker Compose — Orchestrates services with one command
- Google Gemini — AI code review engine
- Pytest — Comprehensive test suite covering core logic

## How It Works

PR Opened -> GitHub Webhook -> FastAPI -> Redis Queue -> Worker -> Gemini AI -> PR Comment

---

## Self-Host Setup

### 1. Clone the Repository
```
git clone https://github.com/MalahimHaseeb/ai-code-reviewer

cd ai-code-reviewer
```

### 2. Configure Environment

```
cp .env.example .env

Fill in your .env with the following variables:

POSTGRES_USER=youruser
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=codereviewdb
DATABASE_URL=postgresql://youruser:yourpassword@db:5432/codereviewdb
REDIS_URL=redis://redis:6379
GEMINI_API_KEY=your_gemini_api_key
GITHUB_WEBHOOK_SECRET=your_webhook_secret
GITHUB_TOKEN=your_github_personal_access_token
```

### 3. Deployment

```
docker compose up --build
```

### 4. Register Your Repository
```
curl -X POST http://localhost:8001/api/repos/register \
  -H "Content-Type: application/json" \
  -d '{"github_repo_name": "your/repo", "github_webhook_secret": "your_secret"}'
```
---

## GitHub Webhook Configuration

Go to your GitHub Repository -> Settings -> Webhooks -> Add webhook:

- Payload URL: https://yourdomain.com/api/webhook
- Content type: application/json
- Secret: (Same value as GITHUB_WEBHOOK_SECRET)
- Events: Select Pull requests only.

---

## Testing

Run the test suite inside the Docker container:
```
docker compose run --rm api pytest app/tests/ -v
```
---
