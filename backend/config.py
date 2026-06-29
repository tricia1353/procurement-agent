"""
配置加载模块
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """应用配置"""

    # 百度 AI Studio
    LLM_ACCESS_TOKEN: str = os.getenv("LLM_ACCESS_TOKEN", "")
    LLM_API_URL: str = os.getenv("LLM_API_URL", "https://aistudio.baidu.com")


    # DigiKey API
    DIGIKEY_CLIENT_ID: str = os.getenv("DIGIKEY_CLIENT_ID", "")
    DIGIKEY_CLIENT_SECRET: str = os.getenv("DIGIKEY_CLIENT_SECRET", "")

    # Mouser API（价格追踪核心）
    MOUSER_API_KEY: str = os.getenv("MOUSER_API_KEY", "44d964f9-558e-4365-87b4-46fedcda1db1")
    MOUSER_API_URL: str = os.getenv("MOUSER_API_URL", "https://api.mouser.com")

    # 电商 API
    LCSC_API_KEY: str = os.getenv("LCSC_API_KEY", "")

    # 服务器
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # 数据库
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/cache.db")
    PRICE_HISTORY_DB: str = os.getenv("PRICE_HISTORY_DB", "./data/price_history.db")


settings = Settings()
