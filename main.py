import json
import os
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI智能伴侣", description="一款基于人工智能的情感陪伴应用", version="1.0.0")

#
PRESETS_FILE_PATH = "data/companion_presets.json"


# 返回类
class ApiResponse(BaseModel):
    code: int = 200
    message: str = "操作成功"
    data: Any = None


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
