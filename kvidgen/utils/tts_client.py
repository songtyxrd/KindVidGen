from typing import Optional

import aiohttp
import base64
import json
import uuid

from kvidgen.core.config import settings


def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


@singleton
class TTSClient:
    def __init__(
        self,
        appid: Optional[str] = None,
        access_token: Optional[str] = None,
        cluster: Optional[str] = None,
        host="openspeech.bytedance.com",
    ):
        self.appid = appid or settings.TTS_APPID
        self.access_token = access_token or settings.TTS_ACCESS_TOKEN
        self.cluster = cluster or settings.TTS_CLUSTER
        self.host = host
        self.api_url = f"https://{host}/api/v1/tts"
        self.header = {"Authorization": f"Bearer;{self.access_token}"}  # noqa

    async def synthesize(
        self,
        text: str,
        save_path: str,
        voice_type="BV001_streaming",
        uid: Optional[str] = "388808087185088",
    ):
        request_json = {
            "app": {
                "appid": self.appid,
                "token": self.access_token,
                "cluster": self.cluster,
            },
            "user": {"uid": uid},
            "audio": {
                "voice_type": voice_type,
                "encoding": "mp3",
                "speed_ratio": 1.1,
                "volume_ratio": 1.0,
                "pitch_ratio": 1.0,
                "emotion": "sad",
            },
            "request": {
                "reqid": str(uuid.uuid4()),
                "text": text,
                "text_type": "plain",
                "operation": "query",
                "with_frontend": 1,
                "frontend_type": "tear",
            },
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url, data=json.dumps(request_json), headers=self.header
            ) as resp:
                resp_json = await resp.json()
                if "data" in resp_json:
                    data = resp_json["data"]
                    with open(save_path, "wb") as file_to_save:
                        file_to_save.write(base64.b64decode(data))
                    return save_path
                return None
