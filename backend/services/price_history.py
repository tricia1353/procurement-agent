"""
价格历史服务
集成 Mouser API + DigiKey API + 定时记录
"""

import httpx
import aiosqlite
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from config import settings


@dataclass
class PriceHistoryPoint:
    """价格历史数据点"""
    model: str
    platform: str
    price: float
    currency: str
    stock: Optional[int]
    recorded_date: str
    recorded_at: str


class PriceHistoryService:
    """价格历史服务
    """

    def __init__(self, db_path: str = "./data/price_history.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库（同步）"""
        import os
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else '.', exist_ok=True)

        with sqlite3.connect(self.db_path) as db:
            # 价格历史表
            db.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    price REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    stock INTEGER,
                    recorded_date TEXT NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 价格趋势汇总表（月度）
            db.execute('''
                CREATE TABLE IF NOT EXISTS price_trend_monthly (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    avg_price REAL NOT NULL,
                    min_price REAL,
                    max_price REAL,
                    data_points INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(model, platform, year, month)
                )
            ''')

            # 创建索引
            db.execute('''
                CREATE INDEX IF NOT EXISTS idx_ph_model_date ON price_history(model, recorded_date)
            ''')
            db.execute('''
                CREATE INDEX IF NOT EXISTS idx_ph_platform ON price_history(platform)
            ''')
            db.execute('''
                CREATE INDEX IF NOT EXISTS idx_pt_model_month ON price_trend_monthly(model, year, month)
            ''')
            db.commit()

    async def record_price(
        self,
        model: str,
        platform: str,
        price: float,
        currency: str = "USD",
        stock: Optional[int] = None
    ) -> bool:
        """
        记录价格数据

        Args:
            model: 物料型号
            platform: 平台名称
            price: 单价
            currency: 币种
            stock: 库存

        Returns:
            是否成功记录
        """
        today = datetime.now().strftime("%Y-%m-%d")

        try:
            async with aiosqlite.connect(self.db_path) as db:
                # 检查今天是否已记录
                cursor = await db.execute('''
                    SELECT id FROM price_history
                    WHERE model = ? AND platform = ? AND recorded_date = ?
                ''', (model.upper(), platform, today))

                if await cursor.fetchone():
                    print(f"⚠️ {model} @ {platform} 今日已记录，跳过")
                    return False

                await db.execute('''
                    INSERT INTO price_history
                    (model, platform, price, currency, stock, recorded_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (model.upper(), platform, price, currency, stock, today))
                await db.commit()

                return True

        except Exception as e:
            print(f"❌ 记录价格失败: {e}")
            return False

    async def get_history(
        self,
        model: str,
        days: int = 180,
        platform: Optional[str] = None
    ) -> List[PriceHistoryPoint]:
        """
        获取历史价格

        Args:
            model: 物料型号
            days: 查询天数
            platform: 平台筛选

        Returns:
            历史价格列表
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('''
                SELECT model, platform, price, currency, stock, recorded_date, recorded_at
                WHERE model = ?
            ''', (model.upper(), platform or 'all', days))

            return [
                PriceHistoryPoint(
                    model=row["model"],
                    platform=row["platform"],
                    price=row["price"],
                    currency=row["currency"],
                    stock=row["stock"],
                    recorded_date=row["recorded_date"],
                    recorded_at=row["recorded_at"]
                )
                for row in await cursor.fetchall()
            ]

    async def get_trend(
        self,
        model: str,
        platform: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        计算价格趋势

        Args:
            model: 物料型号
            platform: 平台筛选

        Returns:
            趋势分析结果
        """
        try:
            history = await self.get_history(model, days=180, platform=platform)

            if len(history) < 2:
                return {
                    "trend": "数据不足",
                    "change_percent": 0,
                    "first_price": None,
                    "last_price": None,
                    "data": []
                }

            first_price = history[0].price
            last_price = history[-1].price
            change_percent = ((last_price - first_price) / first_price * 100)

            if change_percent > 5:
                trend = "上涨"
            elif change_percent < -5:
                trend = "下降"
            else:
                trend = "平稳"

            return {
                "trend": trend,
                "change_percent": round(change_percent, 1),
                "first_price": first_price,
                "last_price": last_price,
                "data_count": len(history),
                "data": [h.__dict__ for h in history]
            }
        except Exception as e:
            return {
                "trend": "计算失败",
                "change_percent": 0,
                "first_price": None,
                "last_price": None,
                "data": [],
                "error": str(e)
            }

    async def get_models_with_history(self) -> List[str]:
        """获取有历史数据的物料型号列表"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT DISTINCT model FROM price_history
                ORDER BY model
            ''')

            return [row[0] for row in await cursor.fetchall()]

    async def get_daily_prices(self, date: str) -> List[Dict]:
        """
        获取某天的价格快照

        Args:
            date: 日期 (YYYY-MM-DD)
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('''
                SELECT model, platform, price, currency, stock
                FROM price_history
                WHERE recorded_date = ?
            ''', (date,))

            return [dict(row) for row in await cursor.fetchall()]

    async def update_monthly_trend(self):
        """更新月度趋势汇总"""
        async with aiosqlite.connect(self.db_path) as db:
            # 获取有数据的日期
            cursor = await db.execute('''
                SELECT DISTINCT
                    DATE(recorded_at, 'start of month') as month_start,
                    model, platform
                FROM price_history
                GROUP BY month_start, model, platform
                ORDER BY month_start ASC
            ''')

            for row in await cursor.fetchall():
                month_start = row[0]
                model = row[1]
                platform = row[2]

                # 获取该月的所有记录
                price_cursor = await db.execute('''
                    SELECT price
                    FROM price_history
                    WHERE model = ? AND platform = ?
                    AND DATE(recorded_at, 'start of month') = ?
                ''', (model, platform, month_start))

                prices = [p[0] for p in await price_cursor.fetchall()]

                if prices:
                    year = int(month_start.split('-')[0])
                    month = int(month_start.split('-')[1])
                    min_price = min(prices)
                    max_price = max(prices)

                    # 更新或插入月度汇总
                    await db.execute('''
                        INSERT OR REPLACE INTO price_trend_monthly
                        (model, platform, year, month, avg_price, min_price, max_price, data_points)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (model, platform, year, month, sum(prices) / len(prices),
                     min_price, max_price, len(prices)))

            await db.commit()

    async def clear_expired_history(self, days_to_keep: int = 365):
        """清理过期历史数据"""
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).strftime("%Y-%m-%d")

        async with aiosqlite.connect(self.db_path) as db:
            result = await db.execute('''
                DELETE FROM price_history WHERE recorded_date < ?
            ''', (cutoff_date,))

            return result.rowcount

    async def get_daily_prices(self, date: str) -> List[Dict]:
        """获取某天的价格快照"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('''
                SELECT model, platform, price, currency, stock
                FROM price_history
                WHERE recorded_date = ?
            ''', (date,))

            return [dict(row) for row in await cursor.fetchall()]

    async def get_models_with_history(self) -> List[str]:
        """获取有历史数据的物料型号列表"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT DISTINCT model FROM price_history
                ORDER BY model
            ''')

            return [row[0] for row in await cursor.fetchall()]


# 全局实例
price_history = PriceHistoryService()