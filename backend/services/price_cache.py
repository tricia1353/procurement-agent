"""
价格缓存服务
"""

import aiosqlite
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List


class PriceCacheService:
    """价格缓存服务（SQLite）"""

    def __init__(self, db_path: str = "./data/cache.db"):
        self.db_path = db_path
        self._initialized = False

    async def init_db(self):
        """初始化数据库"""
        if self._initialized:
            return

        async with aiosqlite.connect(self.db_path) as db:
            # 价格缓存表
            await db.execute('''
                CREATE TABLE IF NOT EXISTS price_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    material_model TEXT NOT NULL,
                    platform TEXT,
                    price REAL,
                    currency TEXT DEFAULT 'CNY',
                    stock INTEGER,
                    data_source TEXT,
                    raw_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            ''')

            # 价格趋势表
            await db.execute('''
                CREATE TABLE IF NOT EXISTS price_trend (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    material_model TEXT NOT NULL,
                    date TEXT NOT NULL,
                    price REAL NOT NULL,
                    platform TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 创建索引
            await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_price_model ON price_cache(material_model)
            ''')
            await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_trend_model ON price_trend(material_model)
            ''')

            await db.commit()

        self._initialized = True

    async def get_price(self, model: str, max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
        """
        获取缓存的价格数据

        Args:
            model: 物料型号
            max_age_hours: 最大缓存时间（小时）

        Returns:
            价格数据或 None
        """
        await self.init_db()

        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('''
                SELECT * FROM price_cache
                WHERE material_model = ?
                AND created_at > ?
                ORDER BY created_at DESC
            ''', (model.upper(), cutoff_time.isoformat()))

            rows = await cursor.fetchall()

            if rows:
                return [dict(row) for row in rows]

        return None

    async def save_price(
        self,
        model: str,
        platform: str,
        price: float,
        currency: str = "CNY",
        stock: Optional[int] = None,
        data_source: str = "api",
        raw_data: Optional[Dict] = None
    ):
        """
        保存价格数据

        Args:
            model: 物料型号
            platform: 平台名称
            price: 价格
            currency: 币种
            stock: 库存
            data_source: 数据来源
            raw_data: 原始数据
        """
        await self.init_db()

        expires_at = datetime.now() + timedelta(hours=24)

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO price_cache
                (material_model, platform, price, currency, stock, data_source, raw_data, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                model.upper(),
                platform,
                price,
                currency,
                stock,
                data_source,
                json.dumps(raw_data) if raw_data else None,
                expires_at.isoformat()
            ))
            await db.commit()

    async def save_trend(
        self,
        model: str,
        date: str,
        price: float,
        platform: Optional[str] = None
    ):
        """
        保存价格趋势数据

        Args:
            model: 物料型号
            date: 日期 (YYYY-MM-DD)
            price: 价格
            platform: 平台
        """
        await self.init_db()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO price_trend (material_model, date, price, platform)
                VALUES (?, ?, ?, ?)
            ''', (model.upper(), date, price, platform))
            await db.commit()

    async def get_trend(self, model: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        获取价格趋势

        Args:
            model: 物料型号
            days: 查询天数

        Returns:
            价格趋势列表
        """
        await self.init_db()

        start_date = datetime.now() - timedelta(days=days)

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('''
                SELECT date, price, platform FROM price_trend
                WHERE material_model = ?
                AND date >= ?
                ORDER BY date ASC
            ''', (model.upper(), start_date.strftime("%Y-%m-%d")))

            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def clear_expired(self):
        """清理过期缓存"""
        await self.init_db()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                DELETE FROM price_cache WHERE expires_at < ?
            ''', (datetime.now().isoformat(),))
            await db.commit()


# 全局实例
price_cache = PriceCacheService()