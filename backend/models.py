"""
Pydantic 数据模型
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# ==================== 枚举类型 ====================

class MaterialCategory(str, Enum):
    """物料类别"""
    CHIP = "芯片"
    LCD = "液晶"
    PANEL = "面板"
    PCB = "PCB"
    PASSIVE = "被动元件"
    CONNECTOR = "连接器"
    OTHER = "其他"


class PriceTrend(str, Enum):
    """价格趋势"""
    UP = "上涨"
    DOWN = "下降"
    STABLE = "平稳"


class SourceType(str, Enum):
    """来源类型"""
    REFERRAL = "熟人推荐"
    CUSTOMER = "客户指定"
    OLD_SUPPLIER = "老供应商"
    WEB_SEARCH = "网络搜索"
    SELF_DEVELOPED = "自主开发"


# ==================== Mouser 价格相关模型 ====================

class PriceBreak(BaseModel):
    """价格梯度"""
    quantity: int = Field(..., description="数量")
    price: str = Field(..., description="价格（原始字符串）")
    currency: str = Field(..., description="币种")


class AvailabilityOnOrder(BaseModel):
    """在途库存"""
    quantity: int = Field(..., description="数量")
    date: str = Field(..., description="预计到货日期")


class ComplianceInfo(BaseModel):
    """合规信息"""
    name: str = Field(..., description="合规名称")
    value: str = Field(..., description="合规值")


class AlternatePackaging(BaseModel):
    """替代包装"""
    mfr_part_number: str = Field(..., description="制造商料号")


class MouserProduct(BaseModel):
    """Mouser 产品信息（完整字段）"""
    # 核心标识
    mouser_part_number: str = Field(..., description="Mouser 料号")
    manufacturer_part_number: str = Field(..., description="制造商料号")
    manufacturer: str = Field(..., description="制造商")

    # 描述与分类
    description: str = Field(default="", description="产品描述")
    category: str = Field(default="", description="产品分类")
    image_path: str = Field(default="", description="产品图片")
    datasheet_url: str = Field(default="", description="数据手册链接")
    product_url: str = Field(default="", description="产品详情链接")

    # 库存
    availability_in_stock: int = Field(default=0, description="现货库存")
    availability_on_order: List[AvailabilityOnOrder] = Field(default=[], description="在途库存")
    factory_stock: int = Field(default=0, description="工厂库存")

    # 价格
    price_breaks: List[PriceBreak] = Field(default=[], description="价格梯度")
    price: str = Field(default="", description="基准价格（第一梯度原始字符串）")
    currency: str = Field(default="", description="币种")

    # 订购信息
    moq: int = Field(default=1, description="最小起订量")
    order_multiple: int = Field(default=1, description="订购倍数")
    lead_time: str = Field(default="", description="交期")
    reeling: bool = Field(default=False, description="卷带供应")
    standard_pack_qty: int = Field(default=0, description="标准包装数量")

    # 封装
    package: str = Field(default="", description="封装")

    # 合规与生命周期
    rohs_status: str = Field(default="", description="RoHS 状态")
    lifecycle_status: str = Field(default="", description="生命周期状态")
    product_compliance: List[ComplianceInfo] = Field(default=[], description="合规信息")

    # 替代
    suggested_replacement: str = Field(default="", description="建议替代型号")
    alternate_packagings: List[AlternatePackaging] = Field(default=[], description="替代包装")

    # 物流
    unit_weight_kg: Optional[float] = Field(default=None, description="重量(kg)")


# ==================== 请求模型 ====================

class PriceSearchRequest(BaseModel):
    """价格搜索请求"""
    model: str = Field(..., description="物料型号")
    category: Optional[MaterialCategory] = Field(None, description="物料类别")


class SupplierSearchRequest(BaseModel):
    """供应商搜索请求"""
    category: str = Field(..., description="物料类别")
    model: Optional[str] = Field(None, description="物料型号")
    region: Optional[str] = Field(None, description="期望地区")
    requirements: Optional[List[str]] = Field(default=[], description="特殊要求")


class QuoteItem(BaseModel):
    """报价项"""
    supplier: str = Field(..., description="供应商名称")
    price: float = Field(..., description="单价")
    currency: str = Field(default="CNY", description="币种")
    moq: int = Field(default=1, description="最小起订量")
    lead_time: Optional[int] = Field(None, description="交期(天)")
    quality_grade: str = Field(default="A", description="质量等级")
    payment_terms: Optional[str] = Field(None, description="付款条件")


class QuoteAnalyzeRequest(BaseModel):
    """报价分析请求"""
    model: str = Field(..., description="物料型号")
    quotes: List[QuoteItem] = Field(..., description="报价列表")


class NegotiationRequest(BaseModel):
    """议价请求"""
    model: str = Field(..., description="物料型号")
    supplier: str = Field(..., description="供应商名称")
    current_price: float = Field(..., description="当前报价")
    target_price: Optional[float] = Field(None, description="目标价格")
    annual_volume: int = Field(default=1000, description="年采购量")
    cooperation_years: int = Field(default=0, description="合作年限")


class ChatRequest(BaseModel):
    """对话请求"""
    message: str = Field(..., description="用户消息")
    context: Optional[dict] = Field(None, description="上下文")


# ==================== 响应模型 ====================

class PlatformPrice(BaseModel):
    """平台价格（旧版兼容）"""
    name: str = Field(..., description="平台名称")
    price: str = Field(..., description="价格")
    currency: str = Field(default="CNY", description="币种")
    stock: Optional[int] = Field(None, description="库存")
    moq: int = Field(default=1, description="最小起订量")
    lead_time: Optional[str] = Field(None, description="交期")
    product_url: Optional[str] = Field(None, description="商品链接")


class MarketOverview(BaseModel):
    """市场概览"""
    avg_price: Optional[float] = Field(None, description="市场均价")
    price_range: List[Optional[float]] = Field(default=[None, None], description="价格区间")
    trend: str = Field(default="平稳", description="价格趋势")


class SubstituteModel(BaseModel):
    """替代型号"""
    model: str = Field(..., description="型号")
    brand: str = Field(..., description="品牌")
    compatibility: str = Field(..., description="兼容性")
    price_advantage: Optional[str] = Field(None, description="价格优势")


class PriceSearchResponse(BaseModel):
    """价格搜索响应（新版）"""
    model: str
    platform: Optional[str] = None
    products: List[MouserProduct] = Field(default=[])
    market_overview: MarketOverview = Field(default_factory=MarketOverview)
    history: List[dict] = Field(default=[])
    mouser_configured: bool = False
    api_used: Optional[str] = None
    data_source: Optional[str] = None
    total_found: int = 0
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class SupplierInfo(BaseModel):
    """供应商信息"""
    name: str
    category: Optional[str] = None
    region: Optional[str] = None
    source: Optional[str] = None
    cooperation_years: Optional[int] = None
    advantages: List[str] = Field(default=[])
    issues: List[str] = Field(default=[])
    rating: Optional[float] = None
    credit_score: Optional[int] = None
    certifications: List[str] = Field(default=[])
    contact: Optional[dict] = None


class SupplierSearchResponse(BaseModel):
    """供应商搜索响应"""
    category: str
    suppliers: List[SupplierInfo] = Field(default=[])
    summary: Optional[dict] = None
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class QuoteAnalysisResult(BaseModel):
    """报价分析结果"""
    supplier: str
    rank: int
    price: float
    price_cny: float
    moq: int
    lead_time: Optional[int]
    diff_from_avg: float
    evaluation: str


class QuoteAnalyzeResponse(BaseModel):
    """报价分析响应"""
    model: str
    market_avg: Optional[float] = None
    quote_avg: float
    price_range: List[float]
    analysis: List[QuoteAnalysisResult]
    recommendation: str
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class NegotiationLeverage(BaseModel):
    """议价筹码"""
    point: str
    importance: str = Field(default="medium", description="重要性: high/medium/low")


class NegotiationScript(BaseModel):
    """谈判话术"""
    scenario: str
    script: str


class NegotiationResponse(BaseModel):
    """议价响应"""
    model: str
    supplier: str
    current_price: float
    market_avg_price: Optional[float] = None
    price_diff_percent: Optional[float] = None
    market_trend: Optional[str] = None
    leverage_points: List[str] = Field(default=[])
    negotiation_scripts: List[str] = Field(default=[])
    suggested_target_price: Optional[float] = None
    strategy: Optional[dict] = None
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ChatResponse(BaseModel):
    """对话响应"""
    message: str
    intent: Optional[str] = None
    tool_used: Optional[str] = None
    data: Optional[dict] = None
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "ok"
    llm_configured: bool = False
    version: str = "1.0.0"


# ==================== 供应商寻源增强模型 ====================

class MaterialRequirement(BaseModel):
    """物料需求信息"""
    model: Optional[str] = Field(None, description="物料型号")
    category: str = Field(..., description="物料类别")
    spec: Optional[str] = Field(None, description="规格参数")
    annual_usage: Optional[int] = Field(None, description="年用量")
    pain_points: List[str] = Field(default=[], description="当前痛点")
    requirements: List[str] = Field(default=[], description="采购要求")
    accept_substitute: bool = Field(default=True, description="是否接受替代品牌")


class SourcingRequest(BaseModel):
    """寻源请求"""
    material: MaterialRequirement = Field(..., description="物料需求")
    current_supplier: Optional[str] = Field(None, description="当前供应商（希望替代）")
    preferred_regions: List[str] = Field(default=[], description="期望地区")


class SupplierMatch(BaseModel):
    """供应商匹配结果"""
    name: str
    region: str
    category: str
    products: List[str] = Field(default=[], description="可供应产品")
    advantages: List[str] = Field(default=[])
    served_clients: List[str] = Field(default=[], description="已服务客户")
    match_score: int = Field(default=0, ge=0, le=100, description="匹配度评分")
    certifications: List[str] = Field(default=[])
    source: str = Field(default="", description="信息来源")
    risk_level: str = Field(default="未知", description="风险等级")
    credit_score: Optional[int] = Field(None, description="信用评分")


class SourcingResponse(BaseModel):
    """寻源响应"""
    material: MaterialRequirement
    suppliers: List[SupplierMatch]
    total_found: int
    search_sources: List[str] = Field(default=[], description="搜索来源")
    search_details: Optional[str] = Field(None, description="搜索详情提示")
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class InterviewQuestion(BaseModel):
    """面谈问题"""
    category: str = Field(..., description="问题类别")
    question: str = Field(..., description="问题内容")
    priority: str = Field(default="medium", description="优先级：high/medium/low")
    context: Optional[str] = Field(None, description="问题背景")


class InterviewQuestionsRequest(BaseModel):
    """面谈问题生成请求"""
    suppliers: List[str] = Field(..., description="选中的供应商名称")
    material: MaterialRequirement = Field(..., description="物料需求")
    focus_areas: List[str] = Field(default=[], description="重点关注领域")


class InterviewQuestionsResponse(BaseModel):
    """面谈问题响应"""
    questions_by_supplier: dict = Field(default_factory=dict, description="按供应商分组的问题")
    common_questions: List[InterviewQuestion] = Field(default=[], description="通用问题")
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
