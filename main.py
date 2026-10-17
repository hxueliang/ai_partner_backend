import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routers import router_presets, router_sessions, router_chat

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
)
app = FastAPI(title="AI智能伴侣", description="一款基于人工智能的情感陪伴应用", version="1.0.0")

app.include_router(router_presets)
app.include_router(router_sessions)
app.include_router(router_chat)


# 统一处理异常信息
@app.exception_handler(Exception)
def handle_exception(request: Request, exc: Exception):
    logging.error(f"处理异常, 请求路径: {request.url}, 异常信息: {exc}")
    return JSONResponse(content={"code": 500, "message": "服务器内部错误"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
