"""
Mouser API 测试脚本
运行方式: python3 test_mouser.py
"""

import httpx
import json

# Mouser API Key
API_KEY = "44d964f9-558e-4365-87b4-46fedcda1db1"

async def test_mouser_search():
    """测试 Mouser API 搜索"""

    url = "https://api.mouser.com/api/v1/search/keyword"

    # 请求参数
    params = {
        "apiKey": API_KEY
    }

    # 请求体
    request_body = {
        "SearchByKeywordRequest": {
            "keyword": "STM32F103C8T6",
            "records": 5,
            "startingRecord": 0,
            "searchWithYourSignUpLanguage": "false"
        }
    }

    print("🔍 正在测试 Mouser API...")
    print(f"请求 URL: {url}")
    print()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                params=params,
                json=request_body,
                headers={"Content-Type": "application/json"}
            )

            print(f"状态码: {response.status_code}")
            print()

            if response.status_code == 200:
                data = response.json()
                print("✅ 请求成功！")
                print()

                # 解析结果
                if "SearchResults" in data:
                    parts = data["SearchResults"].get("Parts", [])
                    print(f"找到 {len(parts)} 个产品:")
                    print()

                    for i, part in enumerate(parts, 1):
                        print(f"产品 {i}:")
                        print(f"  Mouser Part Number: {part.get('MouserPartNumber')}")
                        print(f"  Manufacturer: {part.get('Manufacturer')}")  # 直接是字符串
                        print(f"  Description: {part.get('Description')}")
                        print(f"  Category: {part.get('Category')}")

                        # 库存信息
                        stock = part.get('AvailabilityInStock') or part.get('FactoryStock') or '0'
                        print(f"  Stock: {stock}")

                        # 价格信息
                        price_breaks = part.get('PriceBreaks', [])
                        if price_breaks:
                            pb = price_breaks[0]
                            print(f"  Price (1pc): {pb.get('Price')} {pb.get('Currency')}")
                            if len(price_breaks) > 1:
                                print(f"  Price (1000pc): {price_breaks[-1].get('Price')} {price_breaks[-1].get('Currency')}")
                        else:
                            print(f"  Price: N/A")

                        print(f"  Min Order Qty: {part.get('Min')}")
                        print(f"  Lead Time: {part.get('LeadTime')}")
                        print(f"  Product URL: {part.get('ProductDetailUrl')}")
                        print()

                else:
                    print("❌ 响应中没有 SearchResults 字段")
                    print(json.dumps(data, indent=2, ensure_ascii=False))

            else:
                print(f"❌ 请求失败")
                print(f"响应内容: {response.text}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_mouser_search())