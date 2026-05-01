from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def review_code(diff: str) -> str:
    prompt = f"""
You are an expert code reviewer. Review the following git diff and provide:
1. A brief summary of what changed
2. Any bugs or issues you found
3. Security concerns if any
4. Suggestions for improvement

Keep your review concise and developer-friendly.

Git Diff:
{diff}
"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text