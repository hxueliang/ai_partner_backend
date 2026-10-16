import logging
from datetime import datetime
import os
from typing import Any
from openai import OpenAI
from pydantic import BaseModel
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import AiPreset, AiSession, AiMessage, get_session
from fastapi.encoders import jsonable_encoder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
)
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


# 加载伴侣预设模板信息
@app.get("/api/presets", summary="加载伴侣预设模板信息")
async def load_presets(session: AsyncSession = Depends(get_session)):
    logging.info("加载伴侣预设模板信息...")

    result = await session.execute(select(AiPreset).order_by(AiPreset.sort_order.asc()))
    result_list = result.scalars().all()
    presets_list = jsonable_encoder(result_list)  # jsonable_encoder：将对象转为json字符串

    return ApiResponse(code=200, message="获取伴侣预设模板信息成功", data=presets_list)


# 创建新会话
@app.post("/api/sessions", summary="创建新会话")
async def create_session(request: CreateSessionRequest, session: AsyncSession = Depends(get_session)):
    # CreateSessionRequest()
    logging.info(f"创建新会话: {request}")

    # 会话名称
    session_name = generate_session_name()
    logging.info(session_name)

    session.add(AiSession(
        session_name=session_name,
        nick_name=request.nick_name,
        nature=request.nature,
        create_time=datetime.now(),
        update_time=datetime.now()
    ))
    await session.commit()

    return ApiResponse(message="创建新会话成功", data=session_name)


# 互AI交互
@app.post("/api/chat", summary="互AI交互")
async def chat(request: ChatRequest, session: AsyncSession = Depends(get_session)):
    logging.info(f"互AI交互: {request}")

    result = await session.execute(select(AiSession).where(AiSession.session_name == request.session_name))
    current_session = result.scalars().one()

    result = await session.execute(select(AiMessage).where(AiMessage.session_id == current_session.id))
    current_messages = result.scalars().all()

    # 系统提示词
    messages = [{"role": "system", "content": SYSTEM_PROMPT_TEMPLATE % (request.nick_name, request.nature)}]

    # 读取当前会话历史聊天列表
    for m in current_messages:
        messages.append({"role": m.role, "content": m.content})

    # 用户提示词
    messages.append({"role": "user", "content": request.message})

    logging.info(f'------> 与ai交互messages：{messages}')

    response = client.chat.completions.create(  # type: ignore
        model="deepseek-flash",
        messages=messages,
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "disabled"}}
    )

    ai_response_message = response.choices[0].message.content or ""

    session.add(AiMessage(
        session_id=current_session.id,
        role='user',
        content=request.message,
        create_time=datetime.now()
    ))
    session.add(AiMessage(
        session_id=current_session.id,
        role='assistant',
        content=ai_response_message,
        create_time=datetime.now()
    ))

    current_session.nick_name = request.nick_name
    current_session.nature = request.nature

    await session.commit()

    return ApiResponse(message="互AI交互成功", data=ai_response_message)


# 加载会话列表
@app.get("/api/sessions")
async def get_session_list(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(AiSession.session_name).order_by(AiSession.update_time.desc()))
    session_list = result.scalars().all()

    return ApiResponse(message="加载会话列表成功", data=session_list)


# 根据会话名获取会话信息
@app.get("/api/sessions/{session_name}", summary="根据会话名获取会话信息")
async def get_session_by_name(session_name, session: AsyncSession = Depends(get_session)):
    logging.info(f"根据会话名获取会话信息: {session_name}"),

    result = await session.execute(select(AiSession).where(session_name == AiSession.session_name))
    current_session: AiSession = result.scalars().one()

    result = await session.execute(select(AiMessage).where(AiMessage.session_id == current_session.id))
    current_messages = result.scalars().all()

    session_data = {
        "session_name": session_name,
        "nick_name": current_session.nick_name,
        "nature": current_session.nature,
        "messages": [{"role": message.role, "content": message.content} for message in current_messages]
    }

    return ApiResponse(messaenge="根据会话名获取会话信息成功", data=session_data)


# 删除指定会话
@app.delete("/api/sessions/{session_name}")
async def delete_session_by_name(session_name, session: AsyncSession = Depends(get_session)):
    logging.info(f"根据会话名删除会话信息: {session_name}")

    # 查询需要删除的session
    result = await session.execute(select(AiSession).where(AiSession.session_name == session_name))
    delete_session = result.scalars().one()
    # 删除session
    await session.execute(delete(AiSession).where(AiSession.session_name == session_name))
    # 删除的session对应有messages
    await session.execute(delete(AiMessage).where(AiMessage.session_id == delete_session.id))

    await session.commit()

    return ApiResponse(message="删除指定会话成功")


# 统一处理异常信息
@app.exception_handler(Exception)
def handle_exception(request: Request, exc: Exception):
    logging.error(f"处理异常, 请求路径: {request.url}, 异常信息: {exc}")
    return JSONResponse(content={"code": 500, "message": "服务器内部错误"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
