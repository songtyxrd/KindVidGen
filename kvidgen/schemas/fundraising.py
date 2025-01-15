from urllib.parse import urlparse

from pydantic import BaseModel
from typing import List, Optional

from pydantic.v1 import Field, validator


class PatientInfo(BaseModel):
    """患者基础信息"""

    fundraiser_name: str = Field(..., description="筹款人姓名")
    fundraiser_patient_relation: str = Field(..., description="筹款人与患者关系")
    patient_name: Optional[str] = Field(..., description="患者姓名")
    patient_age: int = Field(..., description="患者年龄")
    patient_gender: str = Field(..., description="患者性别")
    illness_type: str = Field(..., description="患病类型")
    hospital_name: str = Field(..., description="医院名称")
    spent_amount: float = Field(..., description="已筹金额")
    target_amount: float = Field(..., description="筹款目标金额")

    def get_fundraiser_info(self):
        return {
            "fundraiser_name": self.fundraiser_name,
            "fundraiser_patient_relation": self.fundraiser_patient_relation,
        }

    def get_patient_info(self):
        return {
            "patient_name": self.patient_name,
            "patient_age": self.patient_age,
            "patient_gender": self.patient_gender,
            "illness_type": self.illness_type,
            "hospital_name": self.hospital_name,
            "spent_amount": self.spent_amount,
            "target_amount": self.target_amount,
        }


class FundraisingRequest(BaseModel):
    """筹款请求参数封装"""

    patient_info: PatientInfo = Field(..., description="患者基础信息")
    fundraising_text: str = Field(..., description="筹款文案")
    image_urls: List[str] = Field(..., description="图片链接列表")
    background_music_url: str = Field(
        ..., description="背景音乐链接", regex=r"^https?://[^\s]+$"
    )

    @validator("image_urls", each_item=True)
    def validate_image_urls(cls, value):  # noqa
        try:
            result = urlparse(value)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Invalid URL")
            if result.scheme not in ["http", "https"]:
                raise ValueError("URL scheme must be http or https")
        except ValueError as e:
            raise ValueError(f"Invalid URL: {value}") from e
        return value
