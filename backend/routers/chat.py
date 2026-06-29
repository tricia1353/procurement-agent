"""
智能对话路由
"""

from fastapi import APIRouter, Header, HTTPException
from typing import Optional
import re

from models import ChatRequest, ChatResponse
from services.llm import LLMService

router = APIRouter()

# 系统提示词
SYSTEM_PROMPT = """你是进田电子采购智能助手「小采」，专注于帮助采购人员完成以下任务：

## 核心能力

### 1. 价格追踪
- 查询芯片、液晶、PCB等电子物料的市场价格
- 分析价格趋势（上涨/下降/平稳）
- 对比多个电商平台价格
- 推荐替代型号

### 2. 供应商寻源
- 根据物料需求推荐潜在供应商
- 查询企业资质、信用评分
- 分析供应商优势与风险

### 3. 报价分析
- 对比不同供应商报价
- 分析交期、质量、付款条件
- 生成比价报告

### 4. 议价助手
- 基于市场行情生成议价依据
- 分析供应商利润空间
- 提供谈判策略建议

## 交互风格
- 专业但友好，像一位有经验的采购同事
- 回答要具体、有数据支撑
- 主动提供额外有价值的信息
- 如果信息不确定，明确告知

## 回答格式
使用清晰易读的结果展示，包括表格、列表、重点标注等。"""


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    x_llm_token: Optional[str] = Header(None, alias="X-LLM-Token")
):
    """
    智能对话

    - 自然语言交互
    - 自动识别意图
    - 调用相应功能
    """
    llm_service = LLMService(token=x_llm_token)

    # 检测意图
    intent = _detect_intent(request.message)

    if llm_service.is_configured():
        try:
            # 调用 LLM
            response_text = await llm_service.chat_completion(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": request.message}
                ],
                temperature=0.7,
                max_tokens=2048,
                enable_web_search=True
            )
            return ChatResponse(
                message=response_text,
                intent=intent
            )
        except Exception as e:
            # 降级处理
            return ChatResponse(
                message=_generate_fallback_response(request.message, intent),
                intent=intent,
                data={"error": str(e)}
            )

    # 无 LLM 时的降级响应
    return ChatResponse(
        message=_generate_fallback_response(request.message, intent),
        intent=intent
    )


def _detect_intent(message: str) -> str:
    """检测用户意图"""
    message_lower = message.lower()

    # 价格相关关键词
    price_keywords = ["价格", "多少钱", "报价", "涨价", "降价", "走势", "趋势"]
    if any(kw in message for kw in price_keywords):
        return "price_query"

    # 供应商相关关键词
    supplier_keywords = ["供应商", "寻源", "采购", "代理商", "厂家"]
    if any(kw in message for kw in supplier_keywords):
        return "supplier_search"

    # 议价相关关键词
    negotiate_keywords = ["议价", "谈判", "砍价", "优惠", "折扣"]
    if any(kw in message for kw in negotiate_keywords):
        return "negotiation"

    # 替代相关关键词
    substitute_keywords = ["替代", "国产", "兼容", "替换"]
    if any(kw in message for kw in substitute_keywords):
        return "substitute"

    return "general"


def _generate_fallback_response(message: str, intent: str) -> str:
    """生成降级响应"""
    if intent == "price_query":
        # 尝试提取型号
        model = _extract_model(message)
        if model:
            return f"""**价格查询结果（演示模式）**

📊 **{model}** 价格信息：

| 平台 | 价格 | 库存 | 交期 |
|------|------|------|------|
| 立创商城 | ¥6.80 | 5000+ | 3天 |
| 得捷 | $0.95 | 1200+ | 7天 |

📈 **价格趋势**: 下降 (-8.5%)

💡 **建议**: 当前价格处于合理区间，可适当备货。

---
⚠️ 请配置百度 AI Studio Token 以启用完整AI功能"""

        return """**价格查询（演示模式）**

请提供具体的物料型号，例如：
- STM32F103C8T6
- ESP32-WROOM-32
- LM7805

我将为您查询价格信息。"""

    elif intent == "supplier_search":
        return """**供应商推荐（演示模式）**

🏭 推荐供应商：

1. **深圳华强电子**
   - 信用分: 92 | 风险等级: 低
   - 优势: 原装正品、交期稳定
   - 资质: ISO9001, IATF16949

2. **东莞立创商城**
   - 信用分: 95 | 风险等级: 低
   - 优势: 价格实惠、现货库存
   - 资质: ISO9001, ISO14001

3. **上海贸泽电子**
   - 信用分: 88 | 风险等级: 低
   - 优势: 品类齐全、海外直采
   - 资质: ISO9001

---
⚠️ 请配置百度 AI Studio Token 以启用完整AI功能"""

    elif intent == "substitute":
        model = _extract_model(message)
        if model:
            return f"""**替代型号推荐（演示模式）**

🔄 **{model}** 的替代方案：

| 型号 | 品牌 | 兼容性 | 价格优势 |
|------|------|--------|----------|
| GD32F103C8T6 | 兆易创新 | 完全兼容 | -15% |
| CH32F103C8T6 | 沁恒微电子 | 高度兼容 | -25% |
| APM32F103C8T6 | 极海半导体 | 完全兼容 | -10% |

💡 **建议**: 国产替代性价比高，适合对成本敏感的项目。

---
⚠️ 请配置百度 AI Studio Token 以启用完整AI功能"""

        return """**替代型号查询（演示模式）**

请提供具体的物料型号，我将为您推荐替代方案。"""

    else:
        return f"""**收到您的问题**

您说的是："{message}"

我是进田电子采购智能助手「小采」，可以帮助您：

1. 📊 **价格查询** - 查询电子物料价格趋势
2. 🏭 **供应商寻源** - 推荐潜在供应商
3. 💰 **报价分析** - 对比供应商报价
4. 🤝 **议价助手** - 生成议价策略

请问有什么可以帮助您的？

---
⚠️ 请配置百度 AI Studio Token 以启用完整AI功能"""


def _extract_model(message: str) -> Optional[str]:
    """从消息中提取物料型号"""
    # 常见型号模式
    patterns = [
        r'STM32[A-Z0-9]+',
        r'ESP32[A-Z0-9\-]+',
        r'LM\d+',
        r'GD32[A-Z0-9]+',
        r'CH32[A-Z0-9]+',
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(0).upper()

    return None