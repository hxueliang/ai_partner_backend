import logging
from datetime import datetime
from fastapi import Depends, APIRouter
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import AiSession, AiMessage, get_session

from app.schemas import ApiResponse, CreateSessionRequest
from app.utils import generate_session_name

router = APIRouter(prefix="/api", tags=["会话管理"])


# 创建新会话
@router.post("/sessions", summary="创建新会话")
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


# 加载会话列表
@router.get("/sessions")
async def get_session_list(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(AiSession.session_name).order_by(AiSession.update_time.desc()))
    session_list = result.scalars().all()

    return ApiResponse(message="加载会话列表成功", data=session_list)


# 根据会话名获取会话信息
@router.get("/sessions/{session_name}", summary="根据会话名获取会话信息")
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
@router.delete("/sessions/{session_name}")
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
