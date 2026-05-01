# AI Code Reviewer

A self-hostable API that automatically reviews GitHub Pull Requests using AI (Google Gemini).

When a PR is opened, GitHub sends a webhook to this service, which queues the job, fetches the diff, runs an AI review, and posts the feedback as a PR comment.

📖 Full writeup: https://blog.malahim.dev/project-showcases/ai-code-reviewer-i-built-a-self-hostable-github-pr-reviewer-with-fastapi-redis-and-docker

## How It Works

PR Opened → GitHub Webhook → FastAPI → Redis Queue → Worker → Gemini → PR Comment → PostgreSQL
GitHub has a ~3s webhook timeout. LLM calls take 5–15s. Redis decouples the two — API returns 200 instantly, worker handles the slow part separately.

## Stack

- FastAPI — webhook receiver, REST API
- PostgreSQL — repos, PR reviews, diff history
- Redis — async job queue
- Docker Compose — runs all 4 services with one command
- Google Gemini — reviews the diff, returns structured feedback
- Pytest — 8 tests covering core logic
- GitHub Actions — CI on push, CD auto-deploys to EC2

## Setup

**1. Clone**

```bash
git clone https://github.com/MalahimHaseeb/ai-code-reviewer
cd ai-code-reviewer
```

**2. Configure**

```bash
cp .env.example .env
```

Fill in `.env`:

```
POSTGRES_USER=youruser
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=codereviewdb
DATABASE_URL=postgresql://youruser:yourpassword@db:5432/codereviewdb
REDIS_URL=redis://redis:6379
GEMINI_API_KEY=your_gemini_api_key
GITHUB_WEBHOOK_SECRET=your_webhook_secret
GITHUB_TOKEN=your_github_personal_access_token
```

**3. Run**

```bash
docker compose up --build
```

**4. Register your repo**

```bash
curl -X POST http://localhost:8001/api/repos/register \
  -H "Content-Type: application/json" \
  -d '{"github_repo_name": "your/repo", "github_webhook_secret": "your_secret"}'
```

**5. Add GitHub webhook**

Go to your repo → Settings → Webhooks → Add webhook:

- Payload URL: `https://yourdomain.com/api/webhook`
- Content type: `application/json`
- Secret: same value as `GITHUB_WEBHOOK_SECRET`
- Events: Pull requests only

## Testing

```bash
docker compose run --rm api pytest app/tests/ -v
```
