from typing import Any
from pydantic import BaseModel


# pydantic 模型
# 返回类
class ApiResponse(BaseModel):
    code: int = 200
    message: str = "操作成功"
    data: Any = None


# 创建会话请求参数
class CreateSessionRequest(BaseModel):
    nick_name: str
    nature: str


# 与AI交互请求参数
class ChatRequest(BaseModel):
    nick_name: str
    nature: str
    session_name: str
    message: str
