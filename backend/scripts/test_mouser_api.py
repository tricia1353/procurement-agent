#!/usr/bin/env python3
"""
Mouser API 快速验证脚本
"""

import os
import asyncio
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.mouser import mouser_api, MouserAPI


async def main():
    console.print(Panel(
        """
        📊 Mouser API 验证
        检查你配置的 API Key 是否能正常调用
        """
    ))

    if not mouser_api.is_configured():
        console.print("[yellow]⚠️ Mouser API 未配置")
        console.print("\n📝 获取方式：")
        console.print("1. 访问 https://developer.mouser.com/")
        console.print("2. 注册/登录")
        console.print("3. My Account → API Keys")
        console.print("4. 创建 API Key")
        console.print("5. 复制 Mouser API Key（32位字母数字字符串）")
        console.print("\n📝 配置到 backend/.env:")
        console.print("MOUSER_API_KEY=your_mouser_key")
        console.print("MOUSER_API_URL=https://api.mouser.com")
        return

    # 测试搜索
    console.print("\n🔍 搜索 STM32F103C8T6...")
    table = Table(title="Mouser API 搜索结果")

    try:
        data = await mouser_api.get_price("STM32F103C8T6")

        if data["success"] and data["products"]:
            for product in data["products"]:
                table.add_row(
                    product["manufacturer"],
                    product["mouser_part_number"],
                    f"{product['price']} {product['currency']}",
                    f"{product['stock']}",
                    f"{product['lead_time']}天",
                    f"{product['min_order_qty']}起",
                    product["lifecycle_status"]
                )

            console.print(table)
            console.print(f"\n💰 最低价: ${data['best_price']}")
            console.print(f"📦 总数: {data['total_found']}")

        else:
            console.print(f"❌ 未找到 STM32F103C8T6")

    except Exception as e:
        console.print(f"❌ 错误: {str(e)}")

    console.print("\n✅ 测试完成")


if __name__ == "__main__":
    asyncio.run(main())