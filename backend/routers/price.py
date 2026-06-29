"""
价格追踪路由 - 集成 Mouser API + 历史数据

返回 Mouser API 原始数据，不做人民币换算，无虚拟数据。
"""

from fastapi import APIRouter, Header, HTTPException, Query, BackgroundTasks
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from services.mouser import MouserAPI, mouser_api
from services.price_history import price_history

router = APIRouter()


class PriceAnalysisRequest(BaseModel):
    """价格分析请求"""
    model: str
    include_history: bool = False


@router.get("/search")
async def search_price(
    model: str = Query(..., description="物料型号"),
    include_history: bool = Query(False, description="是否包含历史数据"),
    x_llm_token: Optional[str] = Header(None, alias="X-LLM-Token"),
    x_mouser_key: Optional[str] = Header(None, alias="X-Mouser-Key")
):
    """
    查询物料价格

    - 使用 Mouser API 获取实时数据
    - 返回原始价格，不做币种换算
    - 包含完整的价格梯度、库存、合规等信息
    - 自动记录价格到历史数据库
    """
    model_upper = model.upper()
    current_mouser = MouserAPI(api_key=x_mouser_key) if x_mouser_key else mouser_api
    result = {
        "model": model_upper,
        "platform": None,
        "products": [],
        "market_overview": {
            "avg_price": None,
            "price_range": [None, None],
            "trend": "平稳"
        },
        "history": [],
        "mouser_configured": current_mouser.is_configured(),
        "api_used": None,
        "data_source": None,
        "total_found": 0
    }

    # 1. 查询历史数据
    if include_history:
        try:
            history = await price_history.get_history(model_upper, days=60)
            if history:
                result["history"] = [
                    {
                        "date": h.recorded_date,
                        "platform": h.platform,
                        "price": h.price,
                        "currency": h.currency,
                        "stock": h.stock
                    }
                    for h in history
                ]

                # 计算历史均价
                prices = [h["price"] for h in history if h["price"] > 0]
                if prices:
                    result["market_overview"]["avg_price"] = round(sum(prices) / len(prices), 4)
                    result["market_overview"]["price_range"] = [min(prices), max(prices)]
        except Exception as e:
            print(f"获取历史数据失败: {e}")

    # 2. 查询 Mouser 实时价格
    if current_mouser.is_configured():
        try:
            print(f"🔄 使用 Mouser API 查询 {model_upper}...")
            mouser_data = await current_mouser.get_price(model_upper)

            if mouser_data["success"]:
                result["platform"] = "Mouser"
                result["products"] = mouser_data["products"]
                result["total_found"] = mouser_data["total_found"]
                result["api_used"] = "mouser"
                result["data_source"] = "Mouser API (实时数据)"

                # 计算市场均价（基于第一梯度价格）
                first_prices = []
                for p in mouser_data["products"]:
                    pb = p.get("price_breaks", [])
                    if pb:
                        try:
                            # 从价格字符串提取数值
                            price_str = pb[0]["price"]
                            price_val = float(price_str.replace("¥", "").replace("$", "").replace("€", "").strip())
                            first_prices.append(price_val)
                        except (ValueError, TypeError):
                            pass

                if first_prices:
                    result["market_overview"]["avg_price"] = round(sum(first_prices) / len(first_prices), 4)
                    result["market_overview"]["price_range"] = [min(first_prices), max(first_prices)]

            else:
                result["api_used"] = "mouser"
                result["data_source"] = f"Mouser API: {mouser_data.get('message', '未找到')}"

        except Exception as e:
            print(f"查询 Mouser 失败: {e}")
            result["data_source"] = f"Mouser API 错误: {str(e)}"

    else:
        result["data_source"] = "Mouser API 未配置"

    # 3. 记录价格到历史（仅记录有数据的产品）
    if result["products"]:
        for product in result["products"]:
            try:
                # 从第一梯度价格提取数值
                pb = product.get("price_breaks", [])
                if pb:
                    price_str = pb[0]["price"]
                    price_val = float(price_str.replace("¥", "").replace("$", "").replace("€", "").strip())
                    await price_history.record_price(
                        model=model_upper,
                        platform="Mouser",
                        price=price_val,
                        currency=pb[0].get("currency", "USD"),
                        stock=product.get("availability_in_stock", 0)
                    )
            except Exception as e:
                print(f"记录价格失败: {e}")

    return result


@router.get("/trend")
async def get_price_trend(
    model: str = Query(..., description="物料型号"),
    days: int = Query(180, description="查询天数"),
    platform: Optional[str] = Query(None, description="平台筛选")
):
    """
    获取价格趋势

    - 从本地历史数据库获取
    - 返回可用于图表的数据
    """
    model_upper = model.upper()

    try:
        trend_data = await price_history.get_trend(model_upper, platform)

        return {
            "success": True,
            "model": model_upper,
            "trend": trend_data["trend"],
            "change_percent": trend_data["change_percent"],
            "first_price": trend_data["first_price"],
            "last_price": trend_data["last_price"],
            "data_count": trend_data["data_count"],
            "data": trend_data["data"]
        }

    except Exception as e:
        return {
            "success": False,
            "model": model_upper,
            "trend": "未知",
            "change_percent": 0,
            "first_price": None,
            "last_price": None,
            "data": [],
            "error": str(e)
        }


@router.get("/history")
async def get_price_history(
    model: str = Query(..., description="物料型号"),
    days: int = Query(30, description="查询天数")
):
    """
    获取价格历史记录
    """
    model_upper = model.upper()

    try:
        history = await price_history.get_history(model_upper, days)

        return {
            "success": True,
            "model": model_upper,
            "count": len(history),
            "data": [
                {
                    "date": h.recorded_date,
                    "platform": h.platform,
                    "price": h.price,
                    "currency": h.currency,
                    "stock": h.stock,
                    "recorded_at": h.recorded_at
                }
                for h in history
            ]
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ==================== 监控管理接口 ====================

@router.get("/watch-list")
async def get_watch_list():
    """
    获取监控物料列表
    """
    try:
        from services.price_scheduler import price_scheduler
        status = price_scheduler.get_status()
        return {
            "watch_list": status["watch_list"],
            "count": status["watch_list_count"],
            "mouser_configured": mouser_api.is_configured(),
            "scheduler_running": status["running"],
            "next_run": status["next_run"],
            "recent_logs": status["recent_logs"]
        }
    except Exception as e:
        return {"error": str(e)}


@router.post("/watch-list/add")
async def add_to_watch_list(
    model: str = Query(..., description="物料型号"),
    background_tasks: BackgroundTasks = None
):
    """
    添加物料到监控列表

    - 添加后立即尝试获取一次价格
    - 之后每天自动记录
    """
    model_upper = model.upper()

    try:
        from services.price_scheduler import price_scheduler
        price_scheduler.add_to_watch_list(model_upper)

        # 立即尝试记录一次
        if mouser_api.is_configured():
            try:
                price_data = await mouser_api.get_price(model_upper)
                if price_data["success"] and price_data["products"]:
                    product = price_data["products"][0]
                    pb = product.get("price_breaks", [])
                    if pb:
                        price_str = pb[0]["price"]
                        price_val = float(price_str.replace("¥", "").replace("$", "").replace("€", "").strip())
                        await price_history.record_price(
                            model=model_upper,
                            platform="Mouser",
                            price=price_val,
                            currency=pb[0].get("currency", "USD"),
                            stock=product.get("availability_in_stock", 0)
                        )
                        return {
                            "success": True,
                            "message": f"已添加 {model_upper} 到监控列表",
                            "initial_price": price_str,
                            "currency": pb[0].get("currency", "")
                        }
            except Exception as e:
                return {
                    "success": True,
                    "message": f"已添加 {model_upper} 到监控列表，但获取初始价格失败: {str(e)}"
                }

        return {
            "success": True,
            "message": f"已添加 {model_upper} 到监控列表。请配置 Mouser API 以获取价格数据。"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/watch-list/remove")
async def remove_from_watch_list(model: str = Query(..., description="物料型号")):
    """
    从监控列表移除
    """
    model_upper = model.upper()

    try:
        from services.price_scheduler import price_scheduler
        price_scheduler.remove_from_watch_list(model_upper)
        return {
            "success": True,
            "message": f"已从监控列表移除 {model_upper}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/record-now")
async def record_now():
    """
    立即执行一次价格记录
    """
    try:
        from services.price_scheduler import price_scheduler

        if not mouser_api.is_configured():
            raise HTTPException(status_code=400, detail="Mouser API 未配置")

        if not price_scheduler.watch_list:
            raise HTTPException(status_code=400, detail="监控列表为空")

        await price_scheduler.run_once()

        logs = price_scheduler.get_logs(10)
        return {
            "success": True,
            "message": "价格记录完成",
            "logs": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scheduler/status")
async def get_scheduler_status():
    """
    获取调度器状态
    """
    try:
        from services.price_scheduler import price_scheduler
        status = price_scheduler.get_status()
        return status
    except Exception as e:
        return {"error": str(e)}


@router.get("/scheduler/logs")
async def get_scheduler_logs(limit: int = Query(20, description="日志条数")):
    """
    获取调度器日志
    """
    try:
        from services.price_scheduler import price_scheduler
        logs = price_scheduler.get_logs(limit)
        return {"logs": logs}
    except Exception as e:
        return {"error": str(e)}


@router.post("/scheduler/start")
async def start_scheduler(
    hour: int = Query(9, description="每天几点执行"),
    minute: int = Query(0, description="分钟")
):
    """
    启动定时调度器
    """
    try:
        from services.price_scheduler import price_scheduler
        await price_scheduler.start(hour=hour, minute=minute)
        return {
            "success": True,
            "message": f"调度器已启动，每天 {hour:02d}:{minute:02d} 自动记录价格"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduler/stop")
async def stop_scheduler():
    """
    停止调度器
    """
    try:
        from services.price_scheduler import price_scheduler
        price_scheduler.stop()
        return {
            "success": True,
            "message": "调度器已停止"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 历史数据管理 ====================

@router.get("/models")
async def get_tracked_models():
    """
    获取有历史数据的物料型号列表
    """
    try:
        from services.price_history import price_history
        models = await price_history.get_models_with_history()
        return {
            "count": len(models),
            "models": models
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/daily/{date}")
async def get_daily_prices(date: str):
    """
    获取某天的价格快照

    Args:
        date: 日期 (YYYY-MM-DD)
    """
    try:
        from services.price_history import price_history
        prices = await price_history.get_daily_prices(date)
        return {
            "date": date,
            "count": len(prices),
            "prices": prices
        }
    except Exception as e:
        return {"error": str(e)}


# ==================== 统计信息 ====================

@router.get("/statistics")
async def get_statistics():
    """
    获取统计数据

    返回:
    - 总监控型号数
    - 总历史记录数
    - 各平台记录数
    - 最近7天记录数
    """
    try:
        from services.price_history import price_history

        # 统计
        models_count = len(await price_history.get_models_with_history())

        # 总记录数
        total_records = 0
        platform_counts = {"Mouser": 0, "DigiKey": 0, "其他": 0}
        recent_days = 7

        for days in range(1, recent_days + 1):
            try:
                daily = await price_history.get_daily_prices(
                    (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
                )
                total_records += daily["count"]
                for p in daily["prices"]:
                    platform = p.get("platform", "其他")
                    if platform in platform_counts:
                        platform_counts[platform] += 1
            except Exception:
                pass

        # 统计所有库存的型号
        low_stock_models = []
        models = await price_history.get_models_with_history()
        for m in models:
            history = await price_history.get_history(m, days=7)
            recent_stocks = [
                h.stock for h in history if h.stock and h.stock < 50
            ]
            if recent_stocks:
                low_stock_models.append({
                    "model": m,
                    "latest_stock": min(recent_stocks),
                })

        return {
            "total_models": models_count,
            "total_records": total_records,
            "platform_counts": platform_counts,
            "low_stock_models": low_stock_models,
            "recent_days": recent_days
        }
    except Exception as e:
        return {"error": str(e)}
