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
    # await session.execute 方法不可以直接调用 .scalars().all() 直接获取结果
    # 因为这里是异步操作，await 只作用于紧跟它后面的第一个表达式，而不是整条链式调用。
    # 而session.execute 方法执行完毕后的结果是一个协程对象，协程对象是没有 scalars方法的。
    # 因此，我们需要等待该协程执行完毕后，拿到运行结果，然后再调用 .scalars().all() 方法。
    presets_list = jsonable_encoder(result_list)  # jsonable_encoder：将对象转为json字符串

    return ApiResponse(code=200, message="获取伴侣预设模板信息成功", data=presets_list)
