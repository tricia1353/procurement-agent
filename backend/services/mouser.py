"""
Mouser API 服务封装
官方文档：https://api.mouser.com/api/docs/ui/index

完整返回 Mouser 原始数据字段，不做人民币换算，保留原始价格。
"""

import httpx
import re
import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from config import settings


@dataclass
class PriceBreak:
    """价格梯度"""
    quantity: int
    price: str       # 保留原始字符串，如 "¥60.68"
    currency: str


@dataclass
class ProductAttribute:
    """产品属性（封装、标准包装数量等）"""
    name: str
    value: str


@dataclass
class ComplianceInfo:
    """合规信息"""
    name: str
    value: str


@dataclass
class AvailabilityOnOrder:
    """在途库存"""
    quantity: int
    date: str


@dataclass
class AlternatePackaging:
    """替代包装/卷带型号"""
    mfr_part_number: str


@dataclass
class UnitWeight:
    """重量"""
    weight: float


@dataclass
class MouserProduct:
    """Mouser 产品信息 — 完整字段"""
    # 核心标识
    mouser_part_number: str = ""
    manufacturer_part_number: str = ""
    manufacturer: str = ""

    # 描述与分类
    description: str = ""
    category: str = ""
    image_path: str = ""
    datasheet_url: str = ""
    product_detail_url: str = ""

    # 库存
    availability_in_stock: int = 0
    availability_on_order: List[AvailabilityOnOrder] = field(default_factory=list)
    factory_stock: int = 0

    # 价格（完整梯度）
    price_breaks: List[PriceBreak] = field(default_factory=list)
    # 统一显示用的基准价格（第一梯度，保留原始字符串）
    unit_price: str = ""
    currency: str = ""

    # 订购信息
    min_order_qty: int = 1
    order_multiple: int = 1
    lead_time: str = ""
    reeling: bool = False
    standard_pack_qty: int = 0

    # 封装
    package: str = ""

    # 合规与生命周期
    rohs_status: str = ""
    lifecycle_status: str = ""
    product_compliance: List[ComplianceInfo] = field(default_factory=list)

    # 替代
    suggested_replacement: str = ""
    alternate_packagings: List[AlternatePackaging] = field(default_factory=list)

    # 物流
    unit_weight_kg: Optional[float] = None


class MouserAPI:
    """
    Mouser API 封装

    免费层级：60次/天
    """

    def __init__(
        self,
        api_key: Optional[str] = None
    ):
        self.api_key = api_key or settings.MOUSER_API_KEY or os.getenv("MOUSER_API_KEY")
        self.base_url = "https://api.mouser.com"

    def is_configured(self) -> bool:
        """检查是否已配置 API Key"""
        return bool(self.api_key)

    async def search(
        self,
        keyword: str,
        record_count: int = 10,
        search_options: str = None
    ) -> Dict[str, Any]:
        """
        搜索产品

        Args:
            keyword: 搜索关键词（型号）
            record_count: 返回数量
            search_options: 搜索选项 (None|Rohs|InStock|RohsAndInStock)
        """
        if not self.is_configured():
            raise ValueError("Mouser API 未配置，请配置 MOUSER_API_KEY")

        url = f"{self.base_url}/api/v1/search/keyword"

        params = {
            "apiKey": self.api_key
        }

        request_body = {
            "SearchByKeywordRequest": {
                "keyword": keyword,
                "records": record_count,
                "startingRecord": 0,
                "searchWithYourSignUpLanguage": "false"
            }
        }

        if search_options:
            request_body["SearchByKeywordRequest"]["searchOptions"] = search_options

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    params=params,
                    json=request_body,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError("Mouser API 认证失败，请检查 API Key")
            elif e.response.status_code == 429:
                raise ValueError("Mouser API 调用次数超限，请稍后重试")
            else:
                raise ValueError(f"Mouser API 错误: {e.response.status_code} - {e.response.text}")

        except Exception as e:
            raise ValueError(f"Mouser API 请求失败: {str(e)}")

    @staticmethod
    def _parse_stock(stock_str: str) -> int:
        """从库存字符串提取数字"""
        if not stock_str:
            return 0
        match = re.search(r'\d+', stock_str)
        return int(match.group()) if match else 0

    @staticmethod
    def _parse_price_breaks(raw_breaks: Optional[List[Dict]]) -> List[PriceBreak]:
        """解析价格梯度"""
        result = []
        if not raw_breaks:
            return result
        for pb in raw_breaks:
            try:
                qty = int(pb.get("Quantity", 0))
            except (ValueError, TypeError):
                qty = 0
            result.append(PriceBreak(
                quantity=qty,
                price=pb.get("Price", "0"),
                currency=pb.get("Currency", "")
            ))
        return result

    @staticmethod
    def _parse_attributes(attrs: Optional[List[Dict]]) -> Dict[str, str]:
        """解析 ProductAttributes 为 key-value dict"""
        result = {}
        if not attrs:
            return result
        for attr in attrs:
            name = attr.get("AttributeName", "")
            value = attr.get("AttributeValue", "")
            if name:
                result[name] = value
        return result

    async def search_products(
        self,
        keyword: str,
        record_count: int = 10,
        in_stock_only: bool = False
    ) -> List[MouserProduct]:
        """
        搜索产品并返回结构化结果（完整字段）

        Args:
            keyword: 搜索关键词
            record_count: 返回数量
            in_stock_only: 仅显示有库存
        """
        search_options = "InStock" if in_stock_only else None
        data = await self.search(keyword, record_count, search_options)

        products = []

        if data and "SearchResults" in data:
            parts = data.get("SearchResults", {}).get("Parts", [])
            total_results = data.get("SearchResults", {}).get("NumberOfResult", 0)

            for item in parts:
                # 库存
                stock_str = item.get('AvailabilityInStock') or item.get('FactoryStock') or '0'
                availability_in_stock = self._parse_stock(stock_str)
                factory_stock = self._parse_stock(item.get('FactoryStock', '0'))

                # 在途库存
                aoo_raw = item.get('AvailabilityOnOrder') or []
                availability_on_order = []
                for aoo in aoo_raw:
                    try:
                        qty = int(aoo.get("Quantity", 0))
                    except (ValueError, TypeError):
                        qty = 0
                    availability_on_order.append(AvailabilityOnOrder(
                        quantity=qty,
                        date=aoo.get("Date", "")
                    ))

                # 价格梯度（完整）
                price_breaks = self._parse_price_breaks(item.get('PriceBreaks') or [])

                # 基准价格（第一梯度）
                unit_price = price_breaks[0].price if price_breaks else ""
                currency = price_breaks[0].currency if price_breaks else ""

                # 产品属性 → 解析 封装、标准包装数量等
                attrs_raw = item.get('ProductAttributes') or []
                attrs = self._parse_attributes(attrs_raw)
                package = attrs.get("封装", "")
                try:
                    standard_pack_qty = int(attrs.get("标准包装数量", "0"))
                except (ValueError, TypeError):
                    standard_pack_qty = 0

                # 合规信息
                compliance_raw = item.get('ProductCompliance') or []
                product_compliance = [
                    ComplianceInfo(name=c.get("ComplianceName", ""), value=c.get("ComplianceValue", ""))
                    for c in compliance_raw
                ]

                # 替代包装
                alt_raw = item.get('AlternatePackagings') or []
                alternate_packagings = [
                    AlternatePackaging(mfr_part_number=a.get("APMfrPN", ""))
                    for a in alt_raw
                ]

                # 重量
                unit_weight = None
                uw_raw = item.get("UnitWeightKg")
                if uw_raw and "UnitWeight" in uw_raw:
                    try:
                        unit_weight = float(uw_raw["UnitWeight"])
                    except (ValueError, TypeError):
                        pass

                # 起订量、倍数
                try:
                    min_order_qty = int(item.get("Min", 1))
                except (ValueError, TypeError):
                    min_order_qty = 1
                try:
                    order_multiple = int(item.get("Mult", 1))
                except (ValueError, TypeError):
                    order_multiple = 1

                product = MouserProduct(
                    mouser_part_number=item.get("MouserPartNumber", ""),
                    manufacturer_part_number=item.get("ManufacturerPartNumber", keyword),
                    manufacturer=item.get("Manufacturer", "Unknown"),
                    description=item.get("Description", ""),
                    category=item.get("Category", ""),
                    image_path=item.get("ImagePath", ""),
                    datasheet_url=item.get("DataSheetUrl", ""),
                    product_detail_url=item.get("ProductDetailUrl", ""),
                    availability_in_stock=availability_in_stock,
                    availability_on_order=availability_on_order,
                    factory_stock=factory_stock,
                    price_breaks=price_breaks,
                    unit_price=unit_price,
                    currency=currency,
                    min_order_qty=min_order_qty,
                    order_multiple=order_multiple,
                    lead_time=item.get("LeadTime", ""),
                    reeling=item.get("Reeling", False),
                    standard_pack_qty=standard_pack_qty,
                    package=package,
                    rohs_status=item.get("ROHSStatus", ""),
                    lifecycle_status=item.get("LifecycleStatus", ""),
                    product_compliance=product_compliance,
                    suggested_replacement=item.get("SuggestedReplacement", ""),
                    alternate_packagings=alternate_packagings,
                    unit_weight_kg=unit_weight
                )
                products.append(product)

        return products

    async def get_price(self, keyword: str) -> Dict[str, Any]:
        """
        获取价格（快捷方法）

        返回 Mouser API 原始数据，不做人民币换算。
        """
        products = await self.search_products(keyword, record_count=5)

        if not products:
            return {
                "success": False,
                "model": keyword,
                "message": f"未找到 {keyword} 的价格信息",
                "platform": "Mouser",
                "total_found": 0
            }

        return {
            "success": True,
            "model": keyword,
            "platform": "Mouser",
            "products": [
                {
                    # 核心标识
                    "mouser_part_number": p.mouser_part_number,
                    "manufacturer_part_number": p.manufacturer_part_number,
                    "manufacturer": p.manufacturer,

                    # 描述与分类
                    "description": p.description,
                    "category": p.category,
                    "image_path": p.image_path,
                    "datasheet_url": p.datasheet_url,
                    "product_url": p.product_detail_url,

                    # 库存
                    "availability_in_stock": p.availability_in_stock,
                    "availability_on_order": [
                        {"quantity": a.quantity, "date": a.date}
                        for a in p.availability_on_order
                    ],
                    "factory_stock": p.factory_stock,

                    # 价格（完整梯度，保留原始字符串与币种）
                    "price_breaks": [
                        {"quantity": pb.quantity, "price": pb.price, "currency": pb.currency}
                        for pb in p.price_breaks
                    ],
                    "price": p.unit_price,       # 第一梯度原始字符串
                    "currency": p.currency,       # 原始币种

                    # 订购信息
                    "moq": p.min_order_qty,
                    "order_multiple": p.order_multiple,
                    "lead_time": p.lead_time,
                    "reeling": p.reeling,
                    "standard_pack_qty": p.standard_pack_qty,

                    # 封装
                    "package": p.package,

                    # 合规与生命周期
                    "rohs_status": p.rohs_status,
                    "lifecycle_status": p.lifecycle_status,
                    "product_compliance": [
                        {"name": c.name, "value": c.value}
                        for c in p.product_compliance
                    ],

                    # 替代
                    "suggested_replacement": p.suggested_replacement,
                    "alternate_packagings": [
                        {"mfr_part_number": a.mfr_part_number}
                        for a in p.alternate_packagings
                    ],

                    # 物流
                    "unit_weight_kg": p.unit_weight_kg,
                }
                for p in products
            ],
            "total_found": len(products)
        }


# 全局实例
mouser_api = MouserAPI()
