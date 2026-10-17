import logging
from datetime import datetime
from fastapi import Depends, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import client, SYSTEM_PROMPT_TEMPLATE
from app.db import AiSession, AiMessage, get_session

from app.schemas import ApiResponse, ChatRequest

router = APIRouter(prefix="/api", tags=["与AI交互"])


# 与AI交互
@router.post("/chat", summary="与AI交互")
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
