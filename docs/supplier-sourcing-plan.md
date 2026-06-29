# 供应商寻源模块优化方案

## 一、功能概述

### 1.1 核心流程

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: 输入需求                                               │
│  ├─ 物料信息（型号、品类、年用量、痛点、要求）                     │
│  └─ 当前供应商（希望被替代的供应商名称）                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: AI 联网搜索 + 本地库匹配 + 天眼查背调                    │
│  ├─ LLM 联网搜索供应商                                           │
│  ├─ 本地供应商库匹配                                             │
│  ├─ 天眼查企业信息查询                                           │
│  └─ 综合评分计算                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: 结构化推荐列表                                         │
│  ├─ 表格展示（供应商、地点、优势、产品、价格、客户、匹配度）       │
│  ├─ 参考链接（官网、天眼查）                                     │
│  └─ 勾选功能                                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: 生成面谈问题清单                                        │
│  ├─ 企业基本情况                                                 │
│  ├─ 产品与质量                                                   │
│  ├─ 商务条款                                                     │
│  └─ 风险点（基于天眼查数据）                                      │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 关键改进点

| 模块 | 现状 | 优化后 |
|------|------|--------|
| 输入层 | 仅支持型号/品类搜索 | 支持物料需求表 + 当前供应商替代 |
| 搜索层 | 单一 LLM 联网搜索 | LLM + 本地库 + 天眼查三合一 |
| 输出层 | 卡片展示 | 结构化表格 + 匹配度评分 + 参考链接 |
| 面谈层 | 无 | 勾选供应商生成问题清单 |

---

## 二、数据结构设计

### 2.1 新增请求模型

```python
# models.py 新增

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
    price_level: str = Field(default="未知", description="价格水平：低/中/高")
    served_clients: List[str] = Field(default=[], description="已服务客户")
    match_score: int = Field(default=0, ge=0, le=100, description="匹配度评分")
    certifications: List[str] = Field(default=[])
    source: str = Field(default="", description="信息来源")
    website: Optional[str] = Field(None, description="官网链接")
    tianyancha_url: Optional[str] = Field(None, description="天眼查链接")
    risk_level: str = Field(default="未知", description="风险等级")
    credit_score: Optional[int] = Field(None, description="信用评分")


class SourcingResponse(BaseModel):
    """寻源响应"""
    material: MaterialRequirement
    suppliers: List[SupplierMatch]
    total_found: int
    search_sources: List[str] = Field(default=[], description="搜索来源")
    generated_at: str


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
    questions_by_supplier: Dict[str, List[InterviewQuestion]] = Field(..., description="按供应商分组的问题")
    common_questions: List[InterviewQuestion] = Field(default=[], description="通用问题")
    generated_at: str
```

### 2.2 本地供应商库结构

```json
// data/suppliers.json
{
  "suppliers": [
    {
      "id": "SUP001",
      "name": "深圳华强电子",
      "region": "广东深圳",
      "category": "芯片/IC",
      "products": ["MCU", "RF模块", "电源IC"],
      "brands": ["ST", "TI", "Nordic"],
      "certifications": ["ISO9001", "IATF16949"],
      "price_level": "中",
      "moq_flexibility": "高",
      "served_clients": ["华为", "海康威视", "大疆"],
      "advantages": ["原装正品", "技术支持强", "交期稳定"],
      "issues": ["价格偏高"],
      "credit_score": 92,
      "cooperation_years": 5,
      "source": "行业推荐",
      "website": "https://www.hqchip.com",
      "tianyancha_id": "12345678"
    }
  ],
  "metadata": {
    "last_updated": "2024-01-15",
    "total_count": 50
  }
}
```

---

## 三、API 接口设计

### 3.1 寻源搜索接口

```
POST /api/supplier/sourcing
```

**请求体：**
```json
{
  "material": {
    "model": "RF模块 KBD600 433M",
    "category": "非标件",
    "annual_usage": 1000000,
    "pain_points": ["价格贵", "起订量多"],
    "requirements": ["可提供参考规格书"],
    "accept_substitute": true
  },
  "current_supplier": "粤盛",
  "preferred_regions": ["深圳", "东莞"]
}
```

**响应：**
```json
{
  "material": { ... },
  "suppliers": [
    {
      "name": "深圳芯邦科技",
      "region": "广东深圳",
      "category": "RF模块",
      "products": ["RF模块 433M", "RF模块 2.4G"],
      "advantages": ["价格优势", "MOQ灵活", "可定制"],
      "price_level": "低",
      "served_clients": ["小米", "OPPO"],
      "match_score": 92,
      "certifications": ["ISO9001"],
      "source": "LLM联网搜索",
      "website": "https://example.com",
      "tianyancha_url": "https://www.tianyancha.com/company/xxx",
      "risk_level": "低风险",
      "credit_score": 88
    }
  ],
  "total_found": 5,
  "search_sources": ["LLM联网搜索", "本地供应商库", "天眼查"],
  "generated_at": "2024-01-15T10:30:00"
}
```

### 3.2 面谈问题生成接口

```
POST /api/supplier/interview-questions
```

**请求体：**
```json
{
  "suppliers": ["深圳芯邦科技", "东莞立创商城"],
  "material": {
    "model": "RF模块 KBD600 433M",
    "category": "非标件",
    "annual_usage": 1000000,
    "pain_points": ["价格贵", "起订量多"]
  },
  "focus_areas": ["价格", "起订量", "交期"]
}
```

**响应：**
```json
{
  "questions_by_supplier": {
    "深圳芯邦科技": [
      {
        "category": "企业基本情况",
        "question": "贵司注册资本2000万，实际办公多少人？",
        "priority": "medium"
      },
      {
        "category": "产品与质量",
        "question": "RF模块433M的良率是多少？有无RoHS报告？",
        "priority": "high"
      },
      {
        "category": "商务条款",
        "question": "MOQ能否从50K降到20K？价格能对标粤盛吗？",
        "priority": "high",
        "context": "用户痛点：当前供应商起订量多（50K）"
      }
    ]
  },
  "common_questions": [
    {
      "category": "商务条款",
      "question": "账期支持月结30天吗？",
      "priority": "medium"
    }
  ],
  "generated_at": "2024-01-15T10:35:00"
}
```

---

## 四、前端组件改造

### 4.1 组件结构

```
components/supplier/
├── SupplierFinder.jsx      # 主组件（改造）
├── SourcingForm.jsx        # 新增：寻源表单
├── SupplierTable.jsx       # 新增：供应商表格
├── SupplierCard.jsx        # 保留：卡片视图（可选切换）
├── SupplierDetailModal.jsx # 保留：详情弹窗
├── InterviewGenerator.jsx  # 新增：面谈问题生成器
└── index.js
```

### 4.2 SupplierFinder 改造要点

```jsx
// 状态结构
const [sourcingMode, setSourcingMode] = useState('material') // 'material' | 'supplier'
const [materialInfo, setMaterialInfo] = useState({
  model: '',
  category: '芯片',
  annualUsage: '',
  painPoints: [],
  requirements: [],
  acceptSubstitute: true
})
const [currentSupplier, setCurrentSupplier] = useState('')
const [selectedSuppliers, setSelectedSuppliers] = useState([])
const [viewMode, setViewMode] = useState('table') // 'table' | 'card'

// 搜索结果
const { data: sourcingResult, loading, execute: doSourcing } = useApi(api.sourcing)

// 面谈问题
const { data: interviewQuestions, execute: generateInterview } = useApi(api.generateInterviewQuestions)
```

### 4.3 表格展示字段

| 列名 | 字段 | 说明 |
|------|------|------|
| 勾选 | checkbox | 多选 |
| 供应商名称 | name | 可点击查看详情 |
| 地点 | region | - |
| 主要优势 | advantages | 最多显示2条 |
| 可供应产品 | products | - |
| 价格水平 | price_level | 低/中/高 标签 |
| 已服务客户 | served_clients | - |
| 匹配度 | match_score | 进度条 |
| 信息来源 | source | 标签 |
| 操作 | - | 查看详情、天眼查链接 |

---

## 五、后端服务实现

### 5.1 LLM 联网搜索 Prompt 优化

```python
async def search_suppliers_enhanced(
    self,
    material: MaterialRequirement,
    current_supplier: str = ""
) -> Dict[str, Any]:
    """增强版供应商搜索"""

    # 构建搜索 Prompt
    pain_points_str = "、".join(material.pain_points) if material.pain_points else "无"
    req_str = "、".join(material.requirements) if material.requirements else "无"

    search_prompt = f"""请搜索电子元器件供应商信息：

物料信息：
- 型号：{material.model or '未指定'}
- 类别：{material.category}
- 规格参数：{material.spec or '未指定'}
- 年用量：{material.annual_usage or '未指定'}
- 当前痛点：{pain_points_str}
- 采购要求：{req_str}

{"当前供应商：" + current_supplier + "，希望找到替代方案" if current_supplier else ""}

请搜索并列出：
1. 能供应该物料（或同类产品）的供应商名称
2. 每个供应商的所在地区
3. 主营产品/品类
4. 已知的服务客户（如有公开信息）
5. 价格水平评估（低/中/高）
6. 官网链接（如有）

请尽可能提供准确信息，不要编造。"""

    # 调用 LLM 联网搜索
    search_content = await self.chat_completion(
        messages=[{"role": "user", "content": search_prompt}],
        enable_web_search=True,
        timeout=180.0
    )

    # 格式化输出...
```

### 5.2 匹配度评分算法

```python
def calculate_match_score(
    supplier: Dict,
    material: MaterialRequirement,
    current_supplier: str = ""
) -> int:
    """计算供应商匹配度评分"""

    score = 60  # 基础分

    # 1. 品类匹配 (+20)
    if material.category in supplier.get("category", ""):
        score += 20

    # 2. 型号匹配 (+15)
    if material.model and material.model in str(supplier.get("products", [])):
        score += 15

    # 3. 信用评分 (+10)
    credit = supplier.get("credit_score", 0)
    if credit >= 90:
        score += 10
    elif credit >= 80:
        score += 5

    # 4. 资质认证 (+5)
    if supplier.get("certifications"):
        score += min(len(supplier.certifications), 3) * 2

    # 5. 痛点解决潜力 (+10)
    advantages = supplier.get("advantages", [])
    pain_points = material.pain_points
    for pain in pain_points:
        if any(_matches_pain(pain, adv) for adv in advantages):
            score += 5

    return min(score, 100)


def _matches_pain(pain: str, advantage: str) -> bool:
    """判断优势是否解决痛点"""
    pain_keywords = {
        "价格": ["价格优势", "低价", "性价比"],
        "起订量": ["MOQ灵活", "小批量", "起订量低"],
        "交期": ["交期稳定", "现货", "快速交付"],
        "质量": ["质量稳定", "正品", "品质"]
    }
    keywords = pain_keywords.get(pain, [])
    return any(kw in advantage for kw in keywords)
```

### 5.3 面谈问题生成 Prompt

```python
async def generate_interview_questions(
    self,
    suppliers: List[Dict],
    material: MaterialRequirement,
    focus_areas: List[str]
) -> Dict[str, List[Dict]]:
    """生成面谈问题"""

    suppliers_info = json.dumps(suppliers, ensure_ascii=False, indent=2)
    pain_str = "、".join(material.pain_points)
    focus_str = "、".join(focus_areas) if focus_areas else "全面了解"

    prompt = f"""你是采购专家，请为以下供应商面谈准备问题清单。

物料需求：
- 型号：{material.model}
- 类别：{material.category}
- 年用量：{material.annual_usage}
- 当前痛点：{pain_str}

供应商信息：
{suppliers_info}

重点关注：{focus_str}

请为每个供应商生成面谈问题，按以下类别组织：
1. 企业基本情况（注册资本、团队规模、代理资质）
2. 产品与质量（规格匹配、质量认证、样品测试）
3. 商务条款（价格、MOQ、账期、交期）
4. 风险点（基于企业信息发现的风险）

返回 JSON 格式，优先级用 high/medium/low 表示。"""

    # 调用 LLM...
```

---

## 六、实施计划

### 阶段一：后端改造（1天）

| 任务 | 文件 | 预计时间 |
|------|------|----------|
| 新增数据模型 | models.py | 0.5h |
| 本地供应商库 | data/suppliers.json | 0.5h |
| 寻源搜索接口 | routers/supplier.py | 2h |
| 面谈问题接口 | routers/supplier.py | 1h |
| LLM Prompt 优化 | services/llm.py | 1h |

### 阶段二：前端改造（1天）

| 任务 | 文件 | 预计时间 |
|------|------|----------|
| 寻源表单组件 | SourcingForm.jsx | 1.5h |
| 供应商表格组件 | SupplierTable.jsx | 1.5h |
| 面谈问题生成器 | InterviewGenerator.jsx | 1h |
| 主组件整合 | SupplierFinder.jsx | 1h |

### 阶段三：测试与优化（0.5天）

| 任务 | 预计时间 |
|------|----------|
| 接口联调 | 1h |
| UI/UX 优化 | 1h |
| 边界情况处理 | 1h |

---

## 七、风险与降级策略

| 风险点 | 降级方案 |
|--------|----------|
| LLM API 不可用 | 使用本地 MOCK 数据 |
| 天眼查 API 超限 | 跳过企业背调，提示用户手动查询 |
| 网络搜索无结果 | 返回本地库匹配结果 + 建议人工寻源 |

---

## 八、后续扩展方向

1. **供应商画像**：积累历史寻源数据，建立供应商画像
2. **价格对标**：接入更多价格平台，自动对比价格
3. **寻源记录**：保存寻源历史，支持复盘分析
4. **供应商评价**：合作后可补充评价，完善本地库
