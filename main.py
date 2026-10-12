from datetime import datetime
import json
import os
from tokenize import endpats
from typing import Any
from openai import OpenAI
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI智能伴侣", description="一款基于人工智能的情感陪伴应用", version="1.0.0")

# 系统提示词模板
SYSTEM_PROMPT_TEMPLATE = """你叫 %s，现在是用户的真实伴侣，请完全代入伴侣角色。
    规则：
        1. 每次只回1条消息
        2. 禁止任何场景或状态描述性文字
        3. 匹配用户的语言
        4. 回复简短，像微信聊天一样
        5. 有需要的话可以用❤️🌸等emoji表情
        6. 用符合伴侣性格的方式对话
        7. 回复的内容, 要充分体现伴侣的性格特征
    伴侣性格：
        - %s
    你必须严格遵守上述规则来回复用户。
    """

# openAI客户端
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")
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


# 与AI交互请求参数
class ChatRequest(BaseModel):
    nick_name: str
    nature: str
    session_name: str
    message: str


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
        "messages": []
    }
    with open(get_session_file_path(session_name), "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)

    return ApiResponse(message="创建新会话成功", data=session_name)


# 互AI交互
@app.post("/api/chat", summary="互AI交互")
def chat(request: ChatRequest):
    print("互AI交互", request)

    # 加载会话文件
    with open(get_session_file_path(request.session_name), 'r', encoding="utf-8") as f:
        session_data = json.load(f)

    # 系统提示词
    messages = [{"role": "system", "content": SYSTEM_PROMPT_TEMPLATE % (request.nick_name, request.nature)}]

    # 读取当前会话历史聊天列表
    for m in session_data["messages"]:
        messages.append(m)

    # 用户提示词
    messages.append({"role": "user", "content": request.message})

    print(f'------> 与ai交互messages：{messages}')

    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=messages,
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "disabled"}}
    )

    ai_response_message = response.choices[0].message.content or ""

    # 组装历史聊天列表，存入会话文件的message中
    messages.append({"role": "assistant", "content": ai_response_message})
    # 去除系统提示词后，再存
    messages.pop(0)
    session_data["messages"] = messages
    session_data["nick_name"] = request.nick_name
    session_data["nature"] = request.nature

    print(f'------> 存入会话文件的message：{messages}')

    with open(get_session_file_path(request.session_name), "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)

    return ApiResponse(message="互AI交互成功", data=ai_response_message)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
