from langchain_openai import ChatOpenAI

from config import settings


def get_llm(temperature: float = 0) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.openrouter_model,
        base_url=settings.openrouter_base_url,
        api_key=settings.openrouter_api_key,
        temperature=temperature,
        default_headers={
            "HTTP-Referer": "https://github.com/sentinel-ai",
            "X-Title": "SentinelAI",
        },
    )
