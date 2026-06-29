#!/usr/bin/env python3
"""
价格追踪测试脚本
演示 DigiKey API 集成
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from services.digikey import digikey_api
from services.price_history import price_history
from services.price_scheduler import price_scheduler

console = Console()


async def test_digikey_api():
    """测试 DigiKey API"""
    console.print("\n[bold blue]测试 DigiKey API[/bold blue]\n")

    if not digikey_api.is_configured():
        console.print("[yellow]⚠️  DigiKey API 未配置[/yellow]")
        console.print("\n获取 DigiKey API Key：")
        console.print("1. 访问: https://developer.digikey.com/")
        console.print("2. 注册开发者账号并登录")
        console.print("3. 进入 My Account → API Keys → Create Key")
        console.print("4. 记录 Client ID 和 Client Secret")
        console.print("\n然后设置环境变量:")
        console.print("export DIGIKEY_CLIENT_ID=your_client_id")
        console.print("export DIGIKEY_CLIENT_SECRET=your_client_secret")
        return False

    # 测试搜索
    test_models = ["STM32F103C8T6", "ESP32-WROOM-32"]

    table = Table(title="DigiKey API 测试结果")
    table.add_column("型号", justify="left", style="cyan")
    table.add_column("是否有货", justify="center")
    table.add_column("最低价($)", justify="right", style="green")
    table.add_column("库存", justify="right")
    table.add_column("厂商")

    for model in test_models:
        try:
            data = await digikey_api.get_price(model)

            if data["success"]:
                product = data["products"][0]
                stock = product["stock"]
                in_stock = "✅" if stock > 0 else "❌"
                table.add_row(
                    model,
                    in_stock,
                    f"${product['price']}",
                    stock,
                    product["manufacturer"]
                )
            else:
                table.add_row(model, "❌", "N/A", "N/A", data.get("message", "未找到"))

        except Exception as e:
            table.add_row(model, "❌", "N/A", "N/A", str(e))

    console.print(table)
    return True


async def test_history_db():
    """测试历史数据库"""
    console.print("\n[bold blue]测试价格历史数据库[/bold blue]\n")

    # 测试记录一条数据
    test_data = [
        ("STM32F103C8T6", "DigiKey", 6.80, "USD", 1000),
        ("ESP32-WROOM-32", "DigiKey", 2.65, "USD", 2000),
        ("LM7805", "DigiKey", 0.95, "USD", 5000),
    ]

    for model, platform, price, currency, stock in test_data:
        await price_history.record_price(
            model=model,
            platform=platform,
            price=price,
            currency=currency,
            stock=stock
        )
        print(f"✅ 记录: {model} @ {platform} - ${price}")

    # 查询历史
    history = await price_history.get_history("STM32F103C8T6", days=10)
    print(f"\n📊 STM32F103C8T6 历史数据（{len(history)}条）")

    # 趋势分析
    trend = await price_history.get_trend("STM32F103C8T6")
    print(f"📈 趋势: {trend['trend']} ({trend['change_percent']}%)")
    print(f"起始价格: ${trend['first_price']} | 最新价格: ${trend['last_price']}")

    # 获取所有有数据的型号
    models = await price_history.get_models_with_history()
    print(f"\n📋 已记录数据的型号（{len(models)}个）:")
    for model in models:
        count = len(await price_history.get_history(model, days=30))
        print(f"  - {model}: {count}条记录")

    return True


async def test_scheduler():
    """测试调度器"""
    console.print("\n[bold blue]测试价格调度器[/bold blue]\n")

    # 添加测试物料
    test_models = ["STM32F103C8T6", "ESP32-WROOM-32"]
    for model in test_models:
        price_scheduler.add_to_watch_list(model)

    console.print(f"📋 监控列表: {price_scheduler.get_watch_list()}")

    # 手动执行一次
    console.print("\n🔄 手动执行一次价格记录...")
    await price_scheduler.run_once()

    # 获取日志
    logs = price_scheduler.get_logs()
    print(f"\n📜️ 最近的日志（{len(logs)}条）:")
    for log in logs[-5:]:
        print(f"  [{log['time']}] {log['level']}: {log['message']}")

    return True


async def interactive_test():
    """交互式测试"""
    console.print(Panel(
        """
        📊 价格追踪 DigiKey API 测试

        请选择测试项目：

        1. 测试 DigiKey API（需要配置 API Key）
        2. 测试历史数据库
        3. 测试调度器
        4. 查看监控列表
        5. 退出
        """,
        title="DigiKey API 集成测试"
    ))

    choice = input("\n请选择 (1-5): ")

    if choice == "1":
        await test_digikey_api()
    elif choice == "2":
        await test_history_db()
    elif choice == "3":
        await test_scheduler()
    elif choice == "4":
        status = price_scheduler.get_status()
        print(f"\n📋 监控列表: {status['watch_list']}")
        print(f"🔄 调度器运行: {status['running']}")
        print(f"⚙️ DigiKey配置: {status['digikey_configured']}")
    elif choice == "5":
        print("\n👋 再见！")
        return
    else:
        print("\n❌ 无效选择")

    # 询问是否继续
    if input("\n是否继续测试？(y/n): ").lower() == "y":
        await interactive_test()


def show_setup_guide():
    """显示配置指南"""
    console.print(Panel("""
📘 DigiKey API 配置指南

📝 获取步骤：
1. 访问 https://developer.digikey.com/
2. 点击 "Sign Up" 注册开发者账号
3. 登录后进入 My Account → API Keys
4. 点击 "Create Key" 创建新的 API Key
5. 记录 Client ID 和 Client Secret

⚙️ 设置环境变量：
export DIGIKEY_CLIENT_ID=your_client_id
export DIGIKEY_CLIENT_SECRET=your_client_secret

📝 或在 backend/.env 中添加：
DIGIKEY_CLIENT_ID=your_client_id
DIGIKEY_CLIENT_SECRET=your_client_secret

🔍 免费额度：
- 免费用户：500次/天
- 超出需要升级付费（个人项目500次/天应该够用）

⏱️ API 端点：
- 搜索: GET https://api.digikey.com/v4/products/search
- 详情: GET https://api.digikey.com/v4/products/{part_number}

📚 文档：
https://developer.digikey.com/docs
    """, title="DigiKey API 配置", border_style="blue"))


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="DigiKey API 测试")
    subparsers = parser.add_subparsers(dest="command")

    # 测试命令
    test_parser = subparsers.add_parser("test", help="测试功能")
    test_sub = test_parser.add_subparsers(dest="test_action")

    test_sub.add_parser("digikey", help="测试 DigiKey API")
    test_sub.add_parser("history", help="测试历史数据库")
    test_sub.add_parser("scheduler", help="测试调度器")

    # 管理命令
    manage_parser = subparsers.add_parser("manage", help="监控管理")
    manage_sub = manage_parser.add_subparsers(dest="manage_action")

    manage_sub.add_parser("add", help="添加监控")
    manage_sub.add_parser("remove", help="移除监控")
    manage_sub.add_parser("list", help="查看监控列表")
    manage_sub.add_parser("status", help="查看调度器状态")

    # 显示配置指南
    parser.add_argument("--guide", action="store_true", help="显示配置指南")

    args = parser.parse_args()

    if args.guide:
        show_setup_guide()
    elif args.command == "test":
        test_action = args.test_action
        if test_action == "digikey":
            await test_digikey_api()
        elif test_action == "history":
            await test_history_db()
        elif test_action == "scheduler":
            await test_scheduler()
        else:
            parser.print_help()
    elif args.command == "manage":
        manage_action = args.manage_action
        if manage_action == "list":
            status = price_scheduler.get_status()
            print(f"\n📊 监控列表: {status['watch_list']}")
            print(f"数量: {status['watch_list_count']}")
            print(f"调度器运行: {status['running']}")
            if status["next_run"]:
                print(f"下次运行: {status['next_run']}")
        elif manage_action == "status":
            status = price_scheduler.get_status()
            print(f"\n📊 状态详情:")
            for key, value in status.items():
                print(f"  {key}: {value}")
        elif manage_action == "add":
            model = input("请输入要监控的物料型号: ").strip()
            if model:
                price_scheduler.add_to_watch_list(model.upper())
                print(f"✅ 已添加 {model.upper()} 到监控列表")
                print(f"\n监控列表: {price_scheduler.get_watch_list()}")
        elif manage_action == "remove":
            model = input("请输入要移除的物料型号: ").strip()
            if model:
                price_scheduler.remove_from_watch_list(model.upper())
                print(f"✅ 已从监控列表移除 {model.upper()}")
                print(f"\n监控列表: {price_scheduler.get_watch_list()}")
        else:
            parser.print_help()
    else:
        # 交互式测试
        await interactive_test()


if __name__ == "__main__":
    asyncio.run(main())