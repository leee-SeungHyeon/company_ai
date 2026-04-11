from config import LLM_PROVIDER, LLM_MODEL, LLM_TEMPERATURE, DENSE_MODEL, OPENAI_BASE_URL


def get_llm():
    if LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)

    if LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE, base_url=OPENAI_BASE_URL)

    if LLM_PROVIDER == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=LLM_MODEL, temperature=LLM_TEMPERATURE)

    raise ValueError(f"지원하지 않는 LLM_PROVIDER: {LLM_PROVIDER} (gemini | openai | anthropic)")


def get_embedding_model():
    if LLM_PROVIDER == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(model=DENSE_MODEL)

    if LLM_PROVIDER in ("openai", "anthropic"):
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model=DENSE_MODEL, base_url=OPENAI_BASE_URL)

    raise ValueError(f"지원하지 않는 LLM_PROVIDER: {LLM_PROVIDER} (gemini | openai | anthropic)")
