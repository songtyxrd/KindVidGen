from __future__ import absolute_import, unicode_literals

from typing import Optional

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str

    SERVER_NAME: str
    SERVER_PORT: Optional[int] = 8000
    WORKERS: Optional[int] = 4

    API_PREFIX: str = "/api"
    VERSION = "1.0.0"
    TIME_ZONE: str = "Asia/Shanghai"

    # tts
    TTS_APPID: str
    TTS_ACCESS_TOKEN: str
    TTS_CLUSTER: str

    # oss
    BUCKET_NAME: str
    ACCESS_KEY_ID: str
    ACCESS_KEY_SECRET: str
    ENDPOINT: str


settings = Settings(_env_file=".env")
