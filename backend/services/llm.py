"""
百度 AI Studio LLM 服务封装
"""

import httpx
import json
import re
from typing import Optional, List, Dict, Any

from config import settings


class LLMService:
    """百度 AI Studio LLM 服务"""

    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.LLM_ACCESS_TOKEN
        self.base_url = settings.LLM_API_URL

    def is_configured(self) -> bool:
        """检查是否已配置 Token"""
        return bool(self.token)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "ernie-4.5-turbo-128k",
        temperature: float = 0.0,
        max_tokens: int = 4096,
        enable_web_search: bool = False,
        timeout: float = 180.0
    ) -> str:
        """
        调用百度 AI Studio LLM API

        Args:
            messages: 对话消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大输出 token 数
            enable_web_search: 是否启用联网搜索
            timeout: 超时时间（秒）

        Returns:
            模型输出的文本内容
        """
        if not self.token:
            raise ValueError("未配置 LLM Access Token")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_completion_tokens": max_tokens,
            "stream": False
        }

        if enable_web_search:
            payload["web_search"] = {"enable": True}

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{self.base_url}/llm/lmapi/v3/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def search_price(self, model: str) -> Dict[str, Any]:
        """
        两步调用：搜索物料价格

        第一步：联网搜索获取价格信息
        第二步：格式化为结构化 JSON
        """
        if not self.is_configured():
            raise ValueError("未配置 LLM Access Token")

        # 第一步：联网搜索
        search_prompt = f"""请搜索"{model}"芯片的价格信息，包括：
1. 各大电商平台的售价（立创商城、得捷DigiKey、贸泽Mouser等）
2. 当前库存情况
3. 近期价格走势
4. 是否有缺货或涨价消息

请列出搜索到的具体信息，包括平台名称、价格、库存等详情。"""

        search_content = await self.chat_completion(
            messages=[{"role": "user", "content": search_prompt}],
            enable_web_search=True,
            timeout=180.0
        )

        # 正则提取关键数据
        prices = self._extract_prices(search_content)
        platforms = self._extract_platforms(search_content)

        # 第二步：格式化输出
        format_prompt = f"""基于以下搜索结果，生成{model}的价格分析报告。

搜索结果原文：
{search_content}

请返回JSON格式（不要代码块）：
{{
  "model": "{model}",
  "marketOverview": {{
    "avgPrice": "市场均价（数字）",
    "priceRange": ["最低价", "最高价"],
    "trend": "价格趋势判断"
  }},
  "platforms": [
    {{
      "name": "平台名称",
      "price": "价格",
      "currency": "币种CNY/USD",
      "stock": "库存数量",
      "moq": "最小起订量"
    }}
  ],
  "analysis": {{
    "priceAdvice": "采购价格建议",
    "timingAdvice": "采购时机建议"
  }}
}}"""

        format_content = await self.chat_completion(
            messages=[{"role": "user", "content": format_prompt}],
            temperature=0.0,
            enable_web_search=False,
            timeout=60.0
        )

        # 解析 JSON
        result = self._parse_json(format_content)
        result["raw_search"] = search_content

        return result

    async def search_suppliers_by_model(self, model: str) -> Dict[str, Any]:
        """
        按产品型号搜索供应商（联网搜索）

        两步调用：
        1. 联网搜索找到该型号的供应商/代理商
        2. 格式化为结构化 JSON

        Args:
            model: 产品型号（如 STM32F103C8T6）

        Returns:
            供应商列表和原始搜索结果
        """
        if not self.is_configured():
            raise ValueError("未配置 LLM Access Token")

        # 第一步：联网搜索
        search_prompt = f"""请搜索电子元器件"{model}"的供应商、代理商、制造商信息，包括：

1. 官方授权代理商（列出公司名称）
2. 主要分销商/贸易商（列出公司名称）
3. 每个供应商的主营业务、所在地区
4. 是否有现货、价格区间（如有）

请尽可能列出搜索到的供应商名称和相关信息。"""

        search_content = await self.chat_completion(
            messages=[{"role": "user", "content": search_prompt}],
            enable_web_search=True,
            timeout=180.0
        )

        # 第二步：格式化输出
        format_prompt = f"""基于以下搜索结果，提取"{model}"的供应商信息，生成JSON格式报告。

搜索结果原文：
{search_content}

请返回JSON格式（不要代码块）：
{{
  "model": "{model}",
  "suppliers": [
    {{
      "name": "供应商名称（必填）",
      "region": "所在地区（省市）",
      "category": "主营品类",
      "mainProducts": ["主要产品"],
      "advantages": ["优势1", "优势2"],
      "source": "来源类型（官方代理/分销商/制造商）"
    }}
  ],
  "summary": {{
    "total_found": 找到的供应商数量,
    "recommendation": "推荐优先联系的供应商及原因"
  }}
}}

注意：只提取明确的供应商名称，不要编造。如果没有找到供应商信息，返回空列表。"""

        format_content = await self.chat_completion(
            messages=[{"role": "user", "content": format_prompt}],
            temperature=0.0,
            enable_web_search=False,
            timeout=60.0
        )

        result = self._parse_json(format_content)
        result["raw_search"] = search_content

        return result

    async def search_suppliers(
        self,
        category: str,
        region: str = "",
        requirements: str = ""
    ) -> Dict[str, Any]:
        """
        两步调用：搜索供应商
        """
        if not self.is_configured():
            raise ValueError("未配置 LLM Access Token")

        region_str = f"{region}地区" if region else ""
        req_str = f"，要求：{requirements}" if requirements else ""

        # 第一步：联网搜索
        search_prompt = f"""请搜索"{category}"{region_str}的供应商信息{req_str}，包括：
1. 主要供应商/代理商名称
2. 公司地址和联系方式
3. 代理品牌或产品线
4. 公司资质认证情况

请列出搜索到的供应商信息。"""

        search_content = await self.chat_completion(
            messages=[{"role": "user", "content": search_prompt}],
            enable_web_search=True,
            timeout=180.0
        )

        # 第二步：格式化输出
        format_prompt = f"""基于以下搜索结果，生成供应商推荐报告。

搜索结果原文：
{search_content}

请返回JSON格式（不要代码块）：
{{
  "category": "{category}",
  "suppliers": [
    {{
      "name": "供应商名称",
      "region": "所在地区",
      "mainProducts": ["主要产品"],
      "certifications": ["资质证书"],
      "advantages": ["主要优势"]
    }}
  ],
  "summary": {{
    "recommendation": "推荐优先联系的供应商"
  }}
}}"""

        format_content = await self.chat_completion(
            messages=[{"role": "user", "content": format_prompt}],
            temperature=0.0,
            enable_web_search=False,
            timeout=60.0
        )

        result = self._parse_json(format_content)
        result["raw_search"] = search_content

        return result

    async def generate_negotiation(
        self,
        model: str,
        supplier: str,
        current_price: float,
        market_avg: Optional[float],
        trend: str,
        volume: int,
        cooperation_years: int
    ) -> Dict[str, Any]:
        """
        生成议价策略（单步调用，不需要联网）
        """
        price_diff = ((current_price - market_avg) / market_avg * 100) if market_avg else 0

        prompt = f"""你是采购议价专家，请根据以下信息生成议价策略：

物料信息：
- 型号：{model}
- 供应商：{supplier}
- 当前报价：¥{current_price}
- 市场均价：¥{market_avg if market_avg else '未知'}
- 报价差异：{price_diff:+.1f}%
- 价格趋势：{trend}

采购背景：
- 年采购量：{volume}件
- 合作年限：{cooperation_years}年

请返回JSON格式（不要代码块）：
{{
  "leveragePoints": ["议价筹码1", "议价筹码2", "议价筹码3"],
  "scripts": ["话术1", "话术2", "话术3"],
  "targetPrice": {{
    "suggested": "建议目标价格",
    "reasoning": "定价依据"
  }},
  "strategy": {{
    "approach": "谈判策略概述"
  }}
}}"""

        content = await self.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="ernie-4.5-0.3b",
            temperature=0.7,
            max_tokens=1024,
            enable_web_search=False,
            timeout=60.0
        )

        return self._parse_json(content)

    def _extract_prices(self, content: str) -> List[float]:
        """从内容中提取价格"""
        pattern = r'[¥$￥]\s*(\d+\.?\d*)'
        matches = re.findall(pattern, content)
        return [float(p) for p in matches if float(p) > 0]

    def _extract_platforms(self, content: str) -> List[str]:
        """从内容中提取平台名称"""
        keywords = ['立创', '得捷', '贸泽', 'DigiKey', 'Mouser', 'LCSC', '淘宝', '1688']
        return [kw for kw in keywords if kw in content]

    def _parse_json(self, content: str) -> Dict[str, Any]:
        """解析 LLM 返回的 JSON"""
        content = content.strip()

        # 去除 markdown 代码块
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        try:
            result = json.loads(content)
            print(f"✅ JSON解析成功，字段: {list(result.keys())}")
            return result
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON解析失败: {e}")
            print(f"📄 原始内容前500字符: {content[:500]}")
            # 尝试修复
            content = re.sub(r',\s*}', '}', content)
            content = re.sub(r',\s*]', ']', content)
            try:
                result = json.loads(content)
                print(f"✅ JSON修复后解析成功")
                return result
            except:
                print(f"❌ JSON修复后仍然失败")
                return {"error": "JSON解析失败", "raw": content[:1000]}

    async def sourcing_search(
        self,
        material: Dict[str, Any],
        current_supplier: str = ""
    ) -> Dict[str, Any]:
        """
        增强版供应商寻源搜索

        Args:
            material: 物料需求信息
            current_supplier: 当前供应商（希望替代）

        Returns:
            供应商列表和搜索结果
        """
        if not self.is_configured():
            raise ValueError("未配置 LLM Access Token")

        # 构建搜索关键词
        model = (material.get('model') or '').strip()
        category = (material.get('category') or '').strip()
        spec = (material.get('spec') or '').strip()

        # 优先用具体型号搜索
        if model:
            search_keywords = f'"{model}"'
            if category:
                search_keywords += f" {category}"
        elif spec:
            search_keywords = f'"{spec}"'
            if category:
                search_keywords += f" {category}"
        elif category:
            search_keywords = f'"{category}"'
        else:
            search_keywords = '"电子元器件供应商"'

        print(f"🔍 搜索关键词: {search_keywords}")

        # 构建搜索 Prompt
        pain_str = "、".join(material.get("pain_points", [])) or "无"
        req_str = "、".join(material.get("requirements", [])) or "无"
        regions_str = "、".join(material.get("preferred_regions", [])) or "不限"

        substitute_note = f"\n当前供应商：{current_supplier}，希望找到业务相似的替代供应商" if current_supplier else ""

        search_prompt = f"""请联网搜索 {search_keywords} 的供应商/代理商信息。

目标物料：{model or category or spec}
痛点：{pain_str}
采购要求：{req_str}
期望地区：{regions_str}{substitute_note}

**搜索重点**：
1. 使用物料的具体型号作为关键词进行精准搜索
2. 搜索该物料/品类的官方授权代理商、直接供应商
3. 搜索能供应该物料的本地化供应商
4. 如果有型号，搜索该型号的官方授权渠道

**需要提取的信息**：
1. 供应商名称（必须准确）
2. 所在地区（省市）
3. 该供应商能供应的与搜索物料**直接相关**的具体产品（不是通用品类）
4. 与该物料相关的技术优势/服务优势
5. 是否有类似项目/客户案例

请详细列出搜索到的供应商信息，特别是他们能供应的具体产品名称。"""

        # 联网搜索
        print("🌐 开始 LLM 联网搜索...")
        search_content = await self.chat_completion(
            messages=[{"role": "user", "content": search_prompt}],
            enable_web_search=True,
            timeout=180.0
        )
        print(f"📄 联网搜索返回内容长度: {len(search_content)} 字符")

        # 格式化输出
        format_prompt = f"""基于以下搜索结果，提取供应商信息生成JSON格式报告。

搜索物料：{model or category or spec}

搜索结果原文：
{search_content}

请返回JSON格式（不要代码块）：
{{
  "suppliers": [
    {{
      "name": "供应商名称（必填）",
      "region": "所在地区（省市）",
      "category": "主营品类",
      "products": ["与搜索物料直接相关的具体产品名称"],
      "advantages": ["与该物料相关的技术/服务优势"],
      "served_clients": ["服务过的相关客户"],
      "source": "联网搜索"
    }}
  ],
  "summary": "搜索结果摘要"
}}

**重要提示**：
1. products 字段必须是与搜索物料直接相关的具体产品，不要写通用品类；例如，如果搜索的是"RF模块 433M"，products应该是["433MHz RF模块", "无线通信模块"]等，而不是["MCU", "电源IC"]
2. 只提取明确能供应搜索物料的供应商，不要编造
3. 如果没有找到匹配的供应商，返回空suppliers列表"""

        print("📋 开始格式化 JSON...")
        format_content = await self.chat_completion(
            messages=[{"role": "user", "content": format_prompt}],
            temperature=0.0,
            enable_web_search=False,
            timeout=60.0
        )

        result = self._parse_json(format_content)
        result["raw_search"] = search_content

        # 输出解析结果摘要
        suppliers_count = len(result.get("suppliers", []))
        print(f"📊 解析完成，找到 {suppliers_count} 个供应商")

        return result

    async def generate_interview_questions(
        self,
        suppliers: List[Dict[str, Any]],
        material: Dict[str, Any],
        focus_areas: List[str]
    ) -> Dict[str, Any]:
        """
        生成面谈问题清单

        Args:
            suppliers: 供应商列表
            material: 物料需求
            focus_areas: 重点关注领域

        Returns:
            按供应商分组的问题清单
        """
        if not self.is_configured():
            raise ValueError("未配置 LLM Access Token")

        suppliers_info = json.dumps(suppliers, ensure_ascii=False, indent=2)
        pain_str = "、".join(material.get("pain_points", [])) or "无"
        focus_str = "、".join(focus_areas) if focus_areas else "全面了解"

        prompt = f"""你是资深采购专家，请为以下供应商面谈准备问题清单。

物料需求：
- 型号：{material.get('model') or '未指定'}
- 类别：{material.get('category') or '未指定'}
- 年用量：{material.get('annual_usage') or '未指定'}
- 当前痛点：{pain_str}

供应商信息：
{suppliers_info}

重点关注领域：{focus_str}

请针对性地根据需求，结合每个供应商现有的信息和缺少的信息，为每个供应商生成面谈问题，按以下类别组织（包含但不限于），：
1. 企业基本情况（注册资本、团队规模、代理资质等）
2. 产品与质量（规格匹配、质量认证、样品测试等）
3. 商务条款（价格、MOQ、账期、交期等）
4. 风险点（基于企业信息发现的风险提示）

返回JSON格式（不要代码块）：
{{
  "questions_by_supplier": {{
    "供应商名称": [
      {{
        "category": "问题类别",
        "question": "具体问题",
        "priority": "high/medium/low",
        "context": "问题背景（可选）"
      }}
    ]
  }},
  "common_questions": [
    {{
      "category": "通用问题类别",
      "question": "通用问题",
      "priority": "high/medium/low"
    }}
  ]
}}

注意：问题要具体、有针对性，能帮助采购做出决策。痛点相关的问题优先级设为high。"""

        content = await self.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4096,
            enable_web_search=False,
            timeout=120.0
        )

        return self._parse_json(content)