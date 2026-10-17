import logging
from fastapi import Depends, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import AiPreset, get_session
from fastapi.encoders import jsonable_encoder

from app.schemas import ApiResponse

router = APIRouter(prefix="/api", tags=["伴侣预设模板信息"])


# 加载伴侣预设模板信息
@router.get("/presets", summary="加载伴侣预设模板信息")
async def load_presets(session: AsyncSession = Depends(get_session)):
    logging.info("加载伴侣预设模板信息...")

    result = await session.execute(select(AiPreset).order_by(AiPreset.sort_order.asc()))
    result_list = result.scalars().all()
    presets_list = jsonable_encoder(result_list)  # jsonable_encoder：将对象转为json字符串

    return ApiResponse(code=200, message="获取伴侣预设模板信息成功", data=presets_list)
