"""
FastAPI 主入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from routers import price, supplier, chat
from models import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("🚀 进田电子采购智能体后端服务启动")
    print(f"📡 LLM API: {'已配置' if settings.LLM_ACCESS_TOKEN else '未配置'}")
    yield
    # 关闭时执行
    print("👋 进田电子采购智能体后端服务关闭")


app = FastAPI(
    title="进田电子采购智能体",
    description="追踪价格趋势、智能寻源",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(price.router, prefix="/api/price", tags=["价格追踪"])
app.include_router(supplier.router, prefix="/api/supplier", tags=["供应商寻源"])
app.include_router(chat.router, prefix="/api/chat", tags=["智能对话"])


@app.get("/", response_model=HealthResponse)
async def root():
    """根路径"""
    return HealthResponse(
        llm_configured=bool(settings.LLM_ACCESS_TOKEN)
    )


@app.get("/api/health", response_model=HealthResponse)
async def health():
    """健康检查"""
    return HealthResponse(
        llm_configured=bool(settings.LLM_ACCESS_TOKEN)
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )