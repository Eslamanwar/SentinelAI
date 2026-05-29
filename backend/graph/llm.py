from langchain_openai import ChatOpenAI

from config import settings


def get_llm(temperature: float = 0) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.litellm_model,
        base_url=settings.litellm_base_url,
        api_key=settings.litellm_api_key,
        temperature=temperature,
    )
