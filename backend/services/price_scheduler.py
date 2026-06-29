"""
价格追踪定时任务调度器
自动定时记录价格数据
"""

import asyncio
from datetime import datetime
from typing import List, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from services.digikey import digikey_api, DigiKeyAPI
from services.price_history import price_history, PriceHistoryService


class PriceTrackerScheduler:
    """价格追踪调度器"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.digikey = digikey_api
        self.history = price_history

        # 需要追踪的物料列表
        self.watch_list: List[str] = []

        # 记录日志
        self.logs: List[dict] = []

    def add_to_watch_list(self, model: str):
        """添加物料到监控列表"""
        model_upper = model.upper()
        if model_upper not in self.watch_list:
            self.watch_list.append(model_upper)
            self._log("info", f"添加监控: {model_upper}")

    def remove_from_watch_list(self, model: str):
        """从监控列表移除"""
        model_upper = model.upper()
        if model_upper in self.watch_list:
            self.watch_list.remove(model_upper)
            self._log("info", f"移除监控: {model_upper}")

    def get_watch_list(self) -> List[str]:
        """获取监控列表"""
        return self.watch_list.copy()

    def _log(self, level: str, message: str):
        """记录日志"""
        self.logs.append({
            "time": datetime.now().isoformat(),
            "level": level,
            "message": message
        })
        # 只保留最近100条日志
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]

        # 打印到控制台
        print(f"[{level.upper()}] {message}")

    async def record_prices_job(self):
        """
        定时任务：记录所有监控物料的价格
        """
        if not self.watch_list:
            self._log("warning", "监控列表为空，跳过记录")
            return

        if not self.digikey.is_configured():
            self._log("warning", "DigiKey API 未配置，跳过记录")
            return

        self._log("info", f"开始记录 {len(self.watch_list)} 个物料价格...")

        success_count = 0
        fail_count = 0

        for model in self.watch_list:
            try:
                # 获取价格
                price_data = await self.digikey.get_price(model)

                if price_data["success"] and price_data["products"]:
                    product = price_data["products"][0]  # 取最低价

                    # 记录到数据库
                    recorded = await self.history.record_price(
                        model=model,
                        platform="DigiKey",
                        price=product["price"],
                        currency=product["currency"],
                        stock=product["stock"]
                    )

                    if recorded:
                        success_count += 1
                        self._log("success", f"✅ {model}: ${product['price']}")
                    else:
                        self._log("info", f"⚠️  {model}: 今日已记录")

                else:
                    fail_count += 1
                    self._log("warning", f"❌ {model}: 未找到价格")

                # 避免请求过快
                await asyncio.sleep(0.5)

            except Exception as e:
                fail_count += 1
                self._log("error", f"❌ {model}: {str(e)}")

        self._log("info", f"记录完成: 成功 {success_count}, 失败 {fail_count}")

    async def start(self, hour: int = 9, minute: int = 0):
        """
        启动调度器

        Args:
            hour: 每天几点执行（默认早上9点）
            minute: 分钟（默认0分）
        """
        # 添加定时任务
        self.scheduler.add_job(
            self.record_prices_job,
            CronTrigger(hour=hour, minute=minute),
            id="daily_price_record",
            replace_existing=True
        )

        self.scheduler.start()
        self._log("info", f"调度器已启动，每天 {hour:02d}:{minute:02d} 自动记录价格")

    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        self._log("info", "调度器已停止")

    async def run_once(self):
        """立即执行一次记录"""
        await self.record_prices_job()

    def get_logs(self, limit: int = 20) -> List[dict]:
        """获取日志"""
        return self.logs[-limit:]

    def get_status(self) -> dict:
        """获取调度器状态"""
        jobs = self.scheduler.get_jobs()

        return {
            "running": self.scheduler.running,
            "watch_list_count": len(self.watch_list),
            "watch_list": self.watch_list,
            "digikey_configured": self.digikey.is_configured(),
            "next_run": str(jobs[0].next_run_time) if jobs else None,
            "recent_logs": self.logs[-5:]
        }


# 全局实例
price_scheduler = PriceTrackerScheduler()


# ==================== 快速启动函数 ====================

async def start_price_tracking(
    watch_list: List[str],
    hour: int = 9,
    minute: int = 0
):
    """
    启动价格追踪

    Args:
        watch_list: 需要监控的物料列表
        hour: 每天几点执行
        minute: 分钟
    """
    # 添加监控物料
    for model in watch_list:
        price_scheduler.add_to_watch_list(model)

    # 启动调度器
    await price_scheduler.start(hour=hour, minute=minute)


if __name__ == "__main__":
    # 测试代码
    async def test():
        # 添加测试物料
        price_scheduler.add_to_watch_list("STM32F103C8T6")
        price_scheduler.add_to_watch_list("ESP32-WROOM-32")

        # 手动执行一次
        await price_scheduler.run_once()

    asyncio.run(test())