"""
DigiKey API 服务封装
官方文档：https://developer.digikey.com/
"""

import httpx
import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from config import settings


@dataclass
class DigiKeyProduct:
    """DigiKey 产品信息"""
    digikey_part_number: str
    manufacturer_part_number: str
    manufacturer: str
    description: str
    unit_price: float
    currency: str
    quantity_available: int
    product_url: str
    datasheet_url: Optional[str] = None
    package: Optional[str] = None
    lead_time: Optional[int] = None


class DigiKeyAPI:
    """
    DigiKey API 封装

    使用方式：
    1. 访问 https://developer.digikey.com/ 注册开发者账号
    2. 在 My Account → API Keys 创建 API Key
    3. 将 Client ID 和 Client Secret 配置到环境变量

    免费层级：500次/天
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None
    ):
        self.client_id = client_id or settings.DIGIKEY_CLIENT_ID or os.getenv("DIGIKEY_CLIENT_ID")
        self.client_secret = client_secret or settings.DIGIKEY_CLIENT_SECRET or os.getenv("DIGIKEY_CLIENT_SECRET")
        self.base_url = "https://api.digikey.com/v4"

    def is_configured(self) -> bool:
        """检查是否已配置 API Key"""
        return bool(self.client_id and self.client_secret)

    async def search(
        self,
        keyword: str,
        record_count: int = 10,
        in_stock_only: bool = False
    ) -> Dict[str, Any]:
        """
        搜索产品

        Args:
            keyword: 搜索关键词（型号）
            record_count: 返回数量
            in_stock_only: 仅显示有库存

        Returns:
            搜索结果
        """
        if not self.is_configured():
            raise ValueError("DigiKey API 未配置，请设置 DIGIKEY_CLIENT_ID 和 DIGIKEY_CLIENT_SECRET")

        url = f"{self.base_url}/products/search"

        headers = {
            "X-DIGIKEY-Client-Id": self.client_id,
            "X-DIGIKEY-Client-Secret": self.client_secret,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        params = {
            "keywords": keyword,
            "recordCount": record_count,
        }

        if in_stock_only:
            params["inStock"] = 0

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError("DigiKey API 认证失败，请检查 Client ID 和 Client Secret")
            elif e.response.status_code == 429:
                raise ValueError("DigiKey API 调用次数超限，请稍后重试")
            else:
                raise ValueError(f"DigiKey API 错误: {e.response.status_code}")

        except Exception as e:
            raise ValueError(f"DigiKey API 请求失败: {str(e)}")

    async def search_products(
        self,
        keyword: str,
        record_count: int = 10
    ) -> List[DigiKeyProduct]:
        """
        搜索产品并返回结构化结果

        Args:
            keyword: 搜索关键词
            record_count: 返回数量

        Returns:
            产品列表
        """
        data = await self.search(keyword, record_count)
        products = []

        if data and "Products" in data:
            for item in data["Products"]:
                try:
                    # 解析价格
                    unit_price = 0.0
                    currency = "USD"
                    if "UnitPrice" in item:
                        unit_price = float(item["UnitPrice"])
                    if "Currency" in item:
                        currency = item["Currency"]

                    product = DigiKeyProduct(
                        digikey_part_number=item.get("DigiKeyPartNumber", ""),
                        manufacturer_part_number=item.get("ManufacturerPartNumber", keyword),
                        manufacturer=item.get("Manufacturer", {}).get("Name", "Unknown"),
                        description=item.get("DetailedDescription", item.get("Description", "")),
                        unit_price=unit_price,
                        currency=currency,
                        quantity_available=item.get("QuantityAvailable", 0),
                        product_url=f"https://www.digikey.com/product-detail/en/{item.get('DigiKeyPartNumber', '')}",
                        datasheet_url=item.get("PrimaryDatasheet"),
                        package=item.get("Parameters", {}).get("Package / Case"),
                        lead_time=None  # DigiKey API 可能不直接返回
                    )
                    products.append(product)
                except Exception as e:
                    print(f"解析产品失败: {e}")
                    continue

        return products

    async def get_product_detail(self, digikey_part_number: str) -> Optional[DigiKeyProduct]:
        """
        获取产品详情

        Args:
            digikey_part_number: DigiKey 料号

        Returns:
            产品详情
        """
        if not self.is_configured():
            raise ValueError("DigiKey API 未配置")

        url = f"{self.base_url}/products/{digikey_part_number}"

        headers = {
            "X-DIGIKEY-Client-Id": self.client_id,
            "X-DIGIKEY-Client-Secret": self.client_secret,
            "Accept": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                if data:
                    return DigiKeyProduct(
                        digikey_part_number=data.get("DigiKeyPartNumber", ""),
                        manufacturer_part_number=data.get("ManufacturerPartNumber", ""),
                        manufacturer=data.get("Manufacturer", {}).get("Name", ""),
                        description=data.get("DetailedDescription", ""),
                        unit_price=float(data.get("UnitPrice", 0)),
                        currency=data.get("Currency", "USD"),
                        quantity_available=data.get("QuantityAvailable", 0),
                        product_url=f"https://www.digikey.com/product-detail/en/{data.get('DigiKeyPartNumber', '')}",
                        datasheet_url=data.get("PrimaryDatasheet"),
                        package=data.get("Parameters", {}).get("Package / Case")
                    )

        except Exception as e:
            print(f"获取产品详情失败: {e}")

        return None

    async def get_price(self, keyword: str) -> Dict[str, Any]:
        """
        获取价格（快捷方法）

        Args:
            keyword: 型号关键词

        Returns:
            价格信息
        """
        products = await self.search_products(keyword, record_count=5)

        if not products:
            return {
                "success": False,
                "model": keyword,
                "message": f"未找到 {keyword} 的价格信息",
                "platform": "DigiKey"
            }

        # 按价格排序
        products.sort(key=lambda x: x.unit_price if x.unit_price > 0 else float('inf'))

        return {
            "success": True,
            "model": keyword,
            "platform": "DigiKey",
            "products": [
                {
                    "digikey_part_number": p.digikey_part_number,
                    "manufacturer_part_number": p.manufacturer_part_number,
                    "manufacturer": p.manufacturer,
                    "price": p.unit_price,
                    "currency": p.currency,
                    "stock": p.quantity_available,
                    "url": p.product_url
                }
                for p in products
            ],
            "best_price": products[0].unit_price if products else None,
            "total_found": len(products)
        }


# 全局实例
digikey_api = DigiKeyAPI()
