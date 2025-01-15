from pydantic import BaseModel
from typing import List


class PatientInfo(BaseModel):
    """患者基础信息"""

    patient_name: str  # 患者姓名
    patient_age: int  # 患者年龄
    patient_gender: str  # 患者性别
    illness_type: str  # 病别类型
    hospital_name: str  # 就医医院名称
    spent_amount: float  # 已花费金额
    target_amount: float  # 筹款目标金额


class FundraisingRequest(BaseModel):
    """筹款请求参数封装"""

    patient_info: PatientInfo  # 患者基础信息
    fundraising_text: str  # 筹款文案
    image_urls: List[str]  # 图片链接列表
