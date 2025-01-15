from threading import RLock
from typing import Optional

import asyncio_oss
import oss2

from kvidgen.core.config import settings


class AliyunOssClient:
    single_lock = RLock()

    def __init__(self) -> None:
        if hasattr(self, "oss_auth"):
            return
        self.oss_auth = oss2.Auth(settings.ACCESS_KEY_ID, settings.ACCESS_KEY_SECRET)
        self.endpoint = settings.ENDPOINT
        self.bucket_name = settings.BUCKET_NAME

    def __new__(cls, *args, **kwargs):
        with AliyunOssClient.single_lock:
            if not hasattr(AliyunOssClient, "_instance"):
                AliyunOssClient._instance = object.__new__(cls)
        return AliyunOssClient._instance

    async def upload_file(self, filepath: str, object_key: str):
        async with asyncio_oss.Bucket(
            self.oss_auth, self.endpoint, self.bucket_name
        ) as bucket:
            await bucket.put_object_from_file(object_key, filepath)

    async def generate_signed_url(
        self, object_key: str, timout: int = 1 * 60 * 10, method: Optional[str] = "GET"
    ):
        async with asyncio_oss.Bucket(
            self.oss_auth, self.endpoint, self.bucket_name
        ) as bucket:
            return await bucket.sign_url(method, object_key, timout)
