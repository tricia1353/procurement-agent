# LLM Prompts — 采购智能体提示词规范

## 1. LLM API 调用方式

### 端点
```
POST https://aistudio.baidu.com/llm/lmapi/v3/chat/completions
```

### 请求头
```
Content-Type: application/json
Authorization: Bearer <access_token>
```

### 关键注意事项

| 项目 | 正确 | 错误（会导致失败） |
|------|------|------|
| 端点路径 | `/llm/lmapi/v3/chat/completions` | `/rpc/2.0/ai_custom/v1/wenxinworkshop/...` |
| token参数名 | `max_completion_tokens` | `max_tokens` |
| 流式参数 | `"stream": false` | 不设置（默认流式） |
| 联网搜索 | `"web_search": {"enable": true}` | `"enable_web_search": true` |

---

## 2. 模型配置

| 功能 | 模型 | temperature | max_completion_tokens | 联网搜索 | 超时 |
|------|------|-------------|----------------------|----------|------|
| 智能对话 | ernie-4.5-turbo-128k | 0.7 | 2048 | 开启 | 120s |
| 价格搜索 | ernie-4.5-turbo-128k | 0.0 | 4096 | 开启 | 180s |
| 供应商推荐 | ernie-4.5-turbo-128k | 0.0 | 4096 | 开启 | 180s |
| 议价策略 | ernie-4.5-0.3b | 0.7 | 1024 | 关闭 | 60s |

---

## 3. 核心策略：两步调用解决编造问题

### 3.1 问题背景

LLM 在被要求输出 JSON 格式时，会编造虚假数据：
- 编造不存在的供应商
- 编造虚假的价格数据
- 编造无法访问的链接

### 3.2 解决方案

```
第一步（联网搜索，自由输出）→ 正则提取关键数据 → 第二步（格式化JSON，数据来自第一步）
```

---

## 4. 价格查询提示词

### 4.1 第一步：联网搜索

```python
def build_price_search_prompt(model: str) -> str:
    return f"""请搜索"{model}"芯片的价格信息，包括：

1. 各大电商平台的售价（立创商城、得捷DigiKey、贸泽Mouser等）
2. 当前库存情况
3. 近期价格走势
4. 是否有缺货或涨价消息

请列出搜索到的具体信息，包括平台名称、价格、库存等详情。直接列出搜索结果即可。"""

# 请求体
{
    "model": "ernie-4.5-turbo-128k",
    "messages": [{"role": "user", "content": build_price_search_prompt("STM32F103C8T6")}],
    "temperature": 0.0,
    "max_completion_tokens": 4096,
    "stream": false,
    "web_search": {"enable": true}
}
```

### 4.2 正则提取关键数据

```python
import re

def extract_price_data(search_content: str) -> dict:
    """从搜索结果中提取价格相关数据"""
    
    # 提取价格
    price_pattern = r'[¥$￥]\s*(\d+\.?\d*)'
    prices = re.findall(price_pattern, search_content)
    prices = [float(p) for p in prices if float(p) > 0]
    
    # 提取库存
    stock_pattern = r'库存[：:]\s*(\d+)'
    stocks = re.findall(stock_pattern, search_content)
    
    # 提取平台
    platforms = []
    platform_keywords = ['立创', '得捷', '贸泽', 'DigiKey', 'Mouser', 'LCSC', '淘宝', '1688']
    for kw in platform_keywords:
        if kw in search_content:
            platforms.append(kw)
    
    return {
        "prices": prices,
        "stocks": stocks,
        "platforms": list(set(platforms)),
        "raw_content": search_content
    }
```

### 4.3 第二步：格式化输出

```python
def build_price_format_prompt(model: str, search_content: str, extracted_data: dict) -> str:
    return f"""基于以下搜索结果，生成{model}的价格分析报告。

搜索结果原文：
{search_content}

从搜索结果中提取的数据：
- 发现的价格: {extracted_data['prices']}
- 提及的平台: {extracted_data['platforms']}

请返回JSON格式（不要代码块）：
{{
  "model": "{model}",
  "marketOverview": {{
    "avgPrice": "计算出的市场均价（数字）",
    "priceRange": ["最低价", "最高价"],
    "trend": "价格趋势判断：上涨/下降/平稳",
    "trendReason": "趋势判断依据"
  }},
  "platforms": [
    {{
      "name": "平台名称（必须是搜索结果中出现的平台）",
      "price": "价格（数字）",
      "currency": "币种CNY/USD",
      "stock": "库存数量（数字，如无则null）",
      "moq": "最小起订量（数字，如无则1）",
      "leadTime": "交期天数（数字，如无则null）",
      "source": "数据来源说明"
    }}
  ],
  "analysis": {{
    "priceAdvice": "基于数据的采购价格建议",
    "timingAdvice": "采购时机建议",
    "riskAlert": "风险提示（如缺货、涨价风险）"
  }},
  "substitutes": [
    {{
      "model": "替代型号",
      "brand": "品牌",
      "compatibility": "兼容性说明",
      "priceAdvantage": "价格优势百分比"
    }}
  ]
}}

严格规则：
1. platforms中的数据必须来自搜索结果，不得编造
2. 价格必须是搜索结果中出现的真实价格
3. 如果搜索结果中没有某个字段的数据，设为null
4. 替代型号如果没有找到，substitutes返回空数组"""
```

---

## 5. 供应商寻源提示词

### 5.1 第一步：联网搜索

```python
def build_supplier_search_prompt(category: str, region: str = "", requirements: str = "") -> str:
    region_str = f"{region}地区" if region else ""
    req_str = f"，要求：{requirements}" if requirements else ""
    
    return f"""请搜索"{category}"{region_str}的供应商信息{req_str}，包括：

1. 主要供应商/代理商名称
2. 公司地址和联系方式（如有）
3. 代理品牌或产品线
4. 公司资质认证情况
5. 行业口碑或评价

请列出搜索到的供应商信息，包括公司名称、所在地、主营业务等。直接列出搜索结果即可。"""
```

### 5.2 第二步：格式化输出

```python
def build_supplier_format_prompt(category: str, search_content: str) -> str:
    return f"""基于以下搜索结果，生成{category}供应商推荐报告。

搜索结果原文：
{search_content}

请返回JSON格式（不要代码块）：
{{
  "category": "{category}",
  "suppliers": [
    {{
      "name": "供应商名称（必须来自搜索结果）",
      "region": "所在地区",
      "mainProducts": ["主要产品/代理品牌"],
      "certifications": ["资质证书"],
      "advantages": ["主要优势"],
      "contact": {{
        "phone": "电话（如有）",
        "address": "地址（如有）"
      }},
      "source": "信息来源"
    }}
  ],
  "summary": {{
    "totalFound": "找到的供应商数量",
    "recommendation": "推荐优先联系的供应商及原因",
    "notes": "寻源注意事项"
  }}
}}

严格规则：
1. 供应商名称必须是搜索结果中出现的真实公司
2. 不要编造联系方式，没有的设为null
3. 优先推荐资质齐全、口碑好的供应商"""
```

---

## 6. 议价策略生成提示词

### 6.1 单步调用（不需要联网搜索）

```python
def build_negotiation_prompt(
    model: str,
    supplier: str,
    current_price: float,
    market_avg: float,
    trend: str,
    volume: int,
    cooperation_years: int
) -> str:
    price_diff = ((current_price - market_avg) / market_avg * 100) if market_avg > 0 else 0
    
    return f"""你是采购议价专家，请根据以下信息生成议价策略：

物料信息：
- 型号：{model}
- 供应商：{supplier}
- 当前报价：¥{current_price}
- 市场均价：¥{market_avg}
- 报价差异：{price_diff:+.1f}%
- 价格趋势：{trend}

采购背景：
- 年采购量：{volume}件
- 合作年限：{cooperation_years}年

请返回JSON格式（不要代码块）：
{{
  "analysis": {{
    "pricePosition": "当前报价在市场中的位置评估",
    "negotiationSpace": "议价空间分析",
    "keyFactors": ["影响议价的关键因素"]
  }},
  "leveragePoints": [
    "议价筹码1：具体说明",
    "议价筹码2：具体说明",
    "议价筹码3：具体说明"
  ],
  "scripts": [
    "话术1：开场白或询价话术",
    "话术2：市场对比话术",
    "话术3：量价谈判话术",
    "话术4：促成话术"
  ],
  "targetPrice": {{
    "suggested": "建议目标价格（数字）",
    "bottom": "底线价格（数字）",
    "reasoning": "定价依据"
  }},
  "strategy": {{
    "approach": "谈判策略概述",
    "timing": "最佳谈判时机",
    "fallbackPlan": "谈不拢时的备选方案"
  }},
  "risks": [
    "谈判风险1",
    "谈判风险2"
  ]
}}

要求：
1. leveragePoints 必须基于实际数据生成，每条15-30字
2. scripts 必须是可直接使用的对话，每条20-50字
3. targetPrice 必须给出具体数字和合理依据
4. 如果报价差异>10%，重点强调市场对比
5. 如果采购量大，重点强调阶梯优惠"""
```

### 6.2 请求体示例

```json
{
  "model": "ernie-4.5-0.3b",
  "messages": [{"role": "user", "content": "..."}],
  "temperature": 0.7,
  "max_completion_tokens": 1024,
  "stream": false
}
```

---

## 7. 智能对话提示词

### 7.1 系统提示词

```python
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
使用清晰的Markdown格式，包括表格、列表、重点标注等。

## 工具调用
当用户的问题需要查询数据时，你会自动调用相应的工具：
- query_price: 查询物料价格
- find_suppliers: 寻找供应商
- analyze_quotes: 分析报价
- generate_negotiation_tips: 生成议价建议"""
```

### 7.2 意图识别与工具调用

```python
def build_chat_prompt(user_message: str, context: dict = None) -> str:
    context_str = ""
    if context:
        context_str = f"\n\n当前上下文信息：\n{json.dumps(context, ensure_ascii=False)}"
    
    return f"""{SYSTEM_PROMPT}

{context_str}

用户问题：{user_message}

请判断用户意图并回答：
1. 如果是价格查询问题，调用 query_price 工具
2. 如果是供应商寻源问题，调用 find_suppliers 工具
3. 如果是报价分析问题，调用 analyze_quotes 工具
4. 如果是议价相关问题，调用 generate_negotiation_tips 工具
5. 如果是通用问题，直接回答

如果需要调用工具，返回JSON格式：
{{"tool": "工具名称", "params": {{...参数}}}}

如果直接回答，返回文本内容即可。"""
```

---

## 8. 响应处理

### 8.1 JSON 解析与清洗

```python
def clean_llm_json(content: str) -> dict:
    """清洗并解析LLM返回的JSON"""
    content = content.strip()
    
    # 去除 markdown 代码块包裹
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    
    content = content.strip()
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        # 尝试修复常见问题
        # 1. 尾逗号问题
        content = re.sub(r',\s*}', '}', content)
        content = re.sub(r',\s*]', ']', content)
        # 2. 单引号问题
        content = content.replace("'", '"')
        return json.loads(content)
```

### 8.2 数据验证

```python
def validate_price_data(data: dict) -> dict:
    """验证价格数据的有效性"""
    if "platforms" in data:
        validated = []
        for p in data["platforms"]:
            # 只保留有有效价格的平台
            if p.get("price") and p["price"] > 0:
                validated.append(p)
        data["platforms"] = validated
    
    if "marketOverview" in data:
        avg = data["marketOverview"].get("avgPrice")
        if avg and (avg <= 0 or avg > 100000):
            data["marketOverview"]["avgPrice"] = None
    
    return data
```

---

## 9. 降级策略

### 9.1 价格查询降级

当 LLM 调用失败时，返回规则生成的数据：

```python
def fallback_price_data(model: str) -> dict:
    """价格查询降级数据"""
    return {
        "model": model,
        "marketOverview": {
            "avgPrice": None,
            "priceRange": [None, None],
            "trend": "未知",
            "trendReason": "数据获取失败，请稍后重试"
        },
        "platforms": [],
        "analysis": {
            "priceAdvice": "建议通过立创商城、得捷等平台手动查询价格",
            "timingAdvice": "当前无法获取趋势信息",
            "riskAlert": None
        },
        "substitutes": [],
        "error": "LLM服务暂时不可用"
    }
```

### 9.2 议价策略降级

```python
def fallback_negotiation_data(model: str, current_price: float, market_avg: float) -> dict:
    """议价策略降级数据"""
    price_diff = ((current_price - market_avg) / market_avg * 100) if market_avg > 0 else 0
    
    leverage = []
    if price_diff > 10:
        leverage.append(f"当前报价高于市场均价{price_diff:.1f}%，存在议价空间")
    elif price_diff > 5:
        leverage.append(f"当前报价略高于市场均价{price_diff:.1f}%")
    else:
        leverage.append("当前报价接近市场均价，议价空间有限")
    
    return {
        "analysis": {
            "pricePosition": f"当前报价与市场均价差异{price_diff:+.1f}%",
            "negotiationSpace": "高" if price_diff > 10 else "中" if price_diff > 5 else "低",
            "keyFactors": ["市场均价对比"]
        },
        "leveragePoints": leverage,
        "scripts": [
            "我们对比了多家供应商的报价，希望您能给一个更有竞争力的价格。",
            "如果价格合适，我们愿意建立长期合作关系。"
        ],
        "targetPrice": {
            "suggested": round(market_avg * 0.95, 2) if market_avg else None,
            "bottom": round(market_avg * 0.90, 2) if market_avg else None,
            "reasoning": "基于市场均价的95折建议"
        },
        "strategy": {
            "approach": "以市场均价为基准进行谈判",
            "timing": "正常工作时间联系供应商",
            "fallbackPlan": "寻找替代供应商或替代物料"
        },
        "risks": ["供应商可能拒绝降价", "可能影响后续合作"],
        "fallback": True
    }
```

---

## 10. 超时配置

| 功能 | 超时时间 | 原因 |
|------|----------|------|
| 价格搜索（第一步） | 180s | 联网搜索+内容生成 |
| 价格格式化（第二步） | 60s | 纯文本处理 |
| 供应商搜索（第一步） | 180s | 联网搜索 |
| 供应商格式化（第二步） | 60s | 纯文本处理 |
| 议价策略生成 | 60s | 不联网，纯推理 |
| 智能对话 | 120s | 可能触发联网搜索 |
