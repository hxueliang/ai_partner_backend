from datetime import datetime
import json
import os
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI智能伴侣", description="一款基于人工智能的情感陪伴应用", version="1.0.0")

#
PRESETS_FILE_PATH = "data/companion_presets.json"
SESSION_DIR = "sessions"

if not os.path.exists(SESSION_DIR):
    os.mkdir(SESSION_DIR)


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


# 公共函数
# 生成会话名
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# 根据会话名获取会话文件路径
def get_session_file_path(session_name):
    return f"sessions/{session_name}.json"


# 加载伴侣预设模板信息
@app.get("/api/presets", summary="加载伴侣预设模板信息")
async def load_presets():
    print("加载伴侣预设模板信息...")
    if not os.path.exists(PRESETS_FILE_PATH):
        return ApiResponse(code=404, message="文件不存在", data=None)
    else:
        with open(PRESETS_FILE_PATH, "r", encoding="utf-8") as f:
            presets_list = json.load(f)

        # 排序
        presets_list.sort(key=lambda x: x["sort_order"])
        return ApiResponse(code=200, message="获取伴侣预设模板信息成功", data=presets_list)


# 创建新会话
@app.post("/api/sessions", summary="创建新会话")
async def create_session(request: CreateSessionRequest):
    # CreateSessionRequest()
    print("创建新会话", request)

    # 会话名称
    session_name = generate_session_name()
    print(session_name)

    # 生成会话json
    session_data = {
        "session_name": session_name,
        "nick_name": request.nick_name,
        "nature": request.nature,
        "message": []
    }
    with open(get_session_file_path(session_name), "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)

    return ApiResponse(message="创建新会话成功", data=session_name)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
