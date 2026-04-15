import os
import httpx
import json
import logging
import re

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEFAULT_MODEL = "llama-3.3-70b-versatile"

logger = logging.getLogger(__name__)

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing")

async def call_groq_llm(
    prompt: str,
    system_prompt: str = "You are a strict JSON extraction engine. Return ONLY valid JSON.",
    model: str = DEFAULT_MODEL,
    retries: int = 1
):
    """
    Calls Groq API with automatic JSON extraction from markdown and retry logic.
    """
    if not prompt or not isinstance(prompt, str):
        raise ValueError("Invalid prompt sent to Groq LLM")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }

    last_error = None
    for attempt in range(retries + 1):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    GROQ_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )

                if response.status_code != 200:
                    logger.error(f"Groq API Error {response.status_code}: {response.text}")
                    raise Exception(response.text)

                result = response.json()
                content = result["choices"][0]["message"]["content"]

                # Extract JSON if it's wrapped in markdown code blocks
                json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
                if json_match:
                    content = json_match.group(1)
                
                # Cleanup and parse
                content = content.strip()
                return json.loads(content)

        except (json.JSONDecodeError, Exception) as e:
            last_error = e
            logger.warning(f"Attempt {attempt + 1} failed for Groq LLM: {str(e)}")
            if attempt < retries:
                # Small retry wait can be added here if needed
                continue
            else:
                logger.error(f"Groq LLM failed after {retries + 1} attempts: {str(e)}")
                if isinstance(e, json.JSONDecodeError):
                    logger.error(f"Final content that failed parsing: {content}")
                raise last_error
