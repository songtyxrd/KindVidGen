from langchain_openai import ChatOpenAI

from kvidgen.core.config import settings
from kvidgen.utils.tts_client import singleton


@singleton
class GPT4o(ChatOpenAI):
    def __init__(self, *args, **kwargs):
        super().__init__(
            model=settings.OPENAI_GPT_MODEL_NAME,
            api_key=settings.OPENAI_GPT_API_KEY,
            base_url=settings.OPENAI_GPT_BASE_URL,
            *args,
            **kwargs
        )
