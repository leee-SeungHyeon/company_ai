from config import LLM_PROVIDER, LLM_MODEL, LLM_TEMPERATURE


def get_llm():
    if LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)

    if LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)

    if LLM_PROVIDER == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=LLM_MODEL, temperature=LLM_TEMPERATURE)

    raise ValueError(f"지원하지 않는 LLM_PROVIDER: {LLM_PROVIDER} (gemini | openai | anthropic)")
