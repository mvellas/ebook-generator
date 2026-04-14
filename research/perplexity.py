from __future__ import annotations
import requests
from datetime import datetime


PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"


def research_topic(theme: str, api_key: str) -> str:
    """Query Perplexity sonar-pro for current context on the given theme."""
    year = datetime.now().year
    query = (
        f"{theme} — current context, key trends, recent data, and expert perspectives as of {year}. "
        f"Provide a comprehensive synthesis suitable for informing a book chapter."
    )

    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a research assistant. Provide a well-structured synthesis of current "
                    "knowledge on the given topic. Focus on facts, trends, and insights. "
                    "Do not include raw URLs or citations lists — integrate the information naturally."
                ),
            },
            {"role": "user", "content": query},
        ],
        "max_tokens": 2000,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(PERPLEXITY_API_URL, json=payload, headers=headers, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]
