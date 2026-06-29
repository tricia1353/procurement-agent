# 采购成本与供应商搜索智能体 — 复刻版产品需求文档（PRD）

> 本文档用于复刻「采购成本与供应商搜索智能体」应用。目标是：仅凭本 PRD，AI 即可实现同样的信息架构、核心功能、交互流程、视觉风格、技术架构、接口契约与运行方式。
>
> 实现时必须优先保证项目能够本地启动、前后端联通、核心流程跑通。

---

## 1. 产品概述

### 1.1 产品名称

**采购成本与供应商搜索智能体**

### 1.2 产品定位

面向电子制造、硬件研发、供应链与采购团队的轻量级采购辅助工具。

产品聚焦两个核心场景：

1. **采购成本分析**
   - 用户输入物料型号。
   - 系统查询 Mouser 产品、价格、库存、交期、封装、RoHS、替代包装等信息。
   - 用户可选择一个或多个产品。
   - 系统生成采购建议或产品对比分析。

2. **供应商搜索**
   - 用户输入物料需求、当前痛点、采购要求、期望地区、当前供应商。
   - 系统搜索并整理供应商列表。
   - 展示供应商名称、地区、优势、可供应产品、客户、资质、风险、信用分、来源。
   - 用户可勾选供应商并生成面谈问题清单。

### 1.3 目标用户

| 用户角色 | 主要诉求 | 产品价值 |
|---|---|---|
| 采购专员 | 快速查物料价格、库存、交期；寻找备选供应商 | 缩短资料收集时间 |
| 采购经理 | 评估采购成本与供应商风险 | 支持采购决策 |
| 供应链负责人 | 建立供应商池，降低单一供应风险 | 发现候选供应商 |
| 硬件/研发工程师 | 查询元器件可得性和替代包装 | 辅助选型 |

### 1.4 核心功能范围

| 模块 | 功能 |
|---|---|
| 采购成本分析 | 物料查询、产品列表、产品选择、价格/库存/交期展示、采购建议、对比分析 |
| 供应商搜索 | 条件表单、供应商搜索、表格视图、卡片视图、详情弹窗 |
| 面谈问题生成 | 勾选供应商后生成结构化面谈问题，支持复制和导出 |
| API 设置 | 配置百度 AI Studio Token、天眼查 Key、Mouser API Key |
| Mock/降级策略 | API 未配置或调用失败时，允许返回结构一致的演示数据，保证课堂复刻可跑通 |

---

## 2. 技术架构

### 2.1 强制技术栈

AI 实现时必须使用以下技术栈，不允许自行替换。

| 层 | 技术 | 禁止替换为 |
|---|---|---|
| 前端框架 | React 18 + Vite | Next.js / Vue / Angular |
| 前端样式 | TailwindCSS | Ant Design / MUI / shadcn/ui |
| 前端请求 | axios | fetch / ky / got |
| Markdown 渲染 | react-markdown | dangerouslySetInnerHTML |
| 图标库 | lucide-react | 其他图标库 |
| 后端框架 | Python FastAPI + Uvicorn | Express / Django / Flask |
| Python 依赖管理 | uv 或 venv 均可，推荐 uv | 全局 pip / sudo pip |
| 数据模型 | Pydantic | dataclass / TypedDict |
| 异步 HTTP | httpx | requests |
| 环境变量 | python-dotenv / pydantic-settings | 硬编码 |
| 本地配置 | 浏览器 localStorage | Cookie / 服务端 session |
| 数据库 | 非必须，默认不使用数据库 | 不要新增复杂数据库功能 |

### 2.2 外部服务

| 服务 | 用途 | 是否必需 |
|---|---|---|
| Mouser API | 查询物料产品、价格、库存、交期 | 推荐配置；未配置走 Mock |
| 百度 AI Studio | 采购建议、供应商搜索、面谈问题生成 | 推荐配置；未配置走模板/演示数据 |
| 天眼查 API | 查询企业资质、信用、风险信息 | 可选增强 |

### 2.3 运行地址与端口

端口不做强制要求，避免不同电脑上因端口占用导致启动失败。

| 服务 | 默认建议 | 要求 |
|---|---|---|
| 前端 | Vite 默认端口，通常为 `http://localhost:3000` 或 `http://localhost:5173` | 以实际启动日志为准 |
| 后端 | 默认可使用 `http://localhost:8000` | 端口必须可通过环境变量或启动参数调整 |
| Vite 代理 | `/api` → 后端实际地址 | 代理目标不能写死，必须可通过环境变量配置 |

推荐约定：

- 后端端口默认值可以是 `8000`，但必须允许通过 `PORT` 环境变量或 `uvicorn --port` 修改。
- 前端端口默认值可以使用 Vite 自动分配，不要求固定为 `3000`。
- 前端访问地址和后端访问地址都以终端启动日志输出为准。
- PRD 中出现的 `localhost:3000`、`localhost:8000` 仅作为示例，不是硬性要求。

### 2.4 技术实现原则

1. 前端所有请求必须通过 `/api` 访问后端。
2. 前端组件禁止直接请求第三方 API。
3. 后端作为代理层，统一访问 Mouser、百度 AI Studio、天眼查。
4. 外部 API Key 可以来自前端 localStorage，也可以来自后端 `.env`。
5. Key 优先级固定为：`前端请求头 > 后端 .env > 空`。
6. 降级数据必须与真实数据结构一致，前端不应针对 mock/fallback 单独写一套渲染逻辑。

---

## 3. 外部 API 集成规范

### 3.1 百度 AI Studio LLM API

| 项 | 内容 |
|---|---|
| Base URL | `https://aistudio.baidu.com` |
| Chat Completions 端点 | `POST /llm/lmapi/v3/chat/completions` |
| 认证方式 | `Authorization: Bearer <access_token>` |
| Token 获取 | `https://aistudio.baidu.com/account/accessToken` |
| 默认模型 | `ernie-4.5-turbo-128k` |

请求格式：

```json
{
  "model": "ernie-4.5-turbo-128k",
  "messages": [
    {
      "role": "user",
      "content": "请生成采购建议..."
    }
  ],
  "temperature": 0.7,
  "max_completion_tokens": 2048,
  "stream": false
}
```

供应商搜索建议开启联网搜索：

```json
{
  "web_search": {
    "enable": true
  }
}
```

响应格式：

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "模型输出内容"
      }
    }
  ]
}
```

百度 AI Studio 避坑：

| 错误写法 | 正确写法 |
|---|---|
| `/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions` | `/llm/lmapi/v3/chat/completions` |
| `max_tokens` | `max_completion_tokens` |
| `enable_web_search: true` | `web_search: { "enable": true }` |
| `stream: true` | `stream: false` |
| 直接假设返回 `data.result` | 应读取 `choices[0].message.content` |

### 3.2 Mouser API

| 项 | 内容 |
|---|---|
| Base URL | `https://api.mouser.com` |
| 认证方式 | Query 参数 `apiKey=<key>` |
| 搜索方式 | POST |
| 说明 | 不使用 `Authorization: Bearer` |

搜索端点：

```text
POST https://api.mouser.com/api/v1/search/keyword?apiKey=<key>
```

请求体：

```json
{
  "SearchByKeywordRequest": {
    "keyword": "STM32F103C8T6",
    "records": 10,
    "startingRecord": 0,
    "searchOptions": "",
    "searchWithYourSignUpLanguage": ""
  }
}
```

Mouser 原始响应核心结构：

```json
{
  "Errors": [],
  "SearchResults": {
    "NumberOfResult": 3,
    "Parts": [
      {
        "MouserPartNumber": "595-STM32F103C8T6",
        "ManufacturerPartNumber": "STM32F103C8T6",
        "Manufacturer": "STMicroelectronics",
        "Description": "ARM Microcontrollers",
        "Category": "Microcontrollers",
        "ImagePath": "https://...",
        "DataSheetUrl": "https://...",
        "ProductDetailUrl": "https://...",
        "Availability": "12,500 In Stock",
        "AvailabilityInStock": "12500",
        "AvailabilityOnOrder": [
          {
            "Quantity": 5000,
            "Date": "07/15/2026"
          }
        ],
        "FactoryStock": 30000,
        "PriceBreaks": [
          {
            "Quantity": 1,
            "Price": "18.50",
            "Currency": "USD"
          }
        ],
        "Min": "1",
        "Mult": "1",
        "LeadTime": "8 Weeks",
        "ReelAllowed": false,
        "StandardPackage": 90,
        "PackagingType": "LQFP-48",
        "ROHSStatus": "RoHS Compliant",
        "LifecycleStatus": "Active",
        "ProductCompliance": [],
        "SuggestedReplacement": "",
        "AlternatePackagings": []
      }
    ]
  }
}
```

后端不能直接把 Mouser 原始结构透传给前端，必须映射为统一产品模型：

```json
{
  "mouser_part_number": "595-STM32F103C8T6",
  "manufacturer_part_number": "STM32F103C8T6",
  "manufacturer": "STMicroelectronics",
  "description": "ARM Microcontrollers",
  "category": "Microcontrollers",
  "image_path": "https://...",
  "datasheet_url": "https://...",
  "product_url": "https://...",
  "availability_in_stock": 12500,
  "availability_on_order": [
    {
      "quantity": 5000,
      "date": "2026-07-15"
    }
  ],
  "factory_stock": 30000,
  "price_breaks": [
    {
      "quantity": 1,
      "price": "18.50",
      "currency": "USD"
    }
  ],
  "price": "18.50",
  "currency": "USD",
  "moq": 1,
  "order_multiple": 1,
  "lead_time": "8 Weeks",
  "reeling": false,
  "standard_pack_qty": 90,
  "package": "LQFP-48",
  "rohs_status": "RoHS Compliant",
  "lifecycle_status": "Active",
  "product_compliance": [],
  "suggested_replacement": "",
  "alternate_packagings": []
}
```

Mouser 避坑：

| 错误写法 | 正确写法 |
|---|---|
| GET `/api/v1/products?keyword=xxx` | POST `/api/v1/search/keyword?apiKey=<key>` |
| `Authorization: Bearer <key>` | Query 参数 `?apiKey=<key>` |
| 读取 `response.products` | 读取 `response.SearchResults.Parts` |
| 把 `AvailabilityInStock` 当数字直接用 | 先清洗字符串后转数字 |
| 把原始 Mouser 响应直接给前端 | 后端必须映射为统一产品模型 |

### 3.3 天眼查 API

| 项 | 内容 |
|---|---|
| Base URL | `https://open.api.tianyancha.com` |
| 认证方式 | Header: `Authorization: <key>` |
| 作用 | 查询企业信息、信用、风险 |
| 是否必需 | 可选增强 |

企业搜索端点：

```text
GET /services/open/search/v2?word=<企业名>
```

响应示例：

```json
{
  "state": "ok",
  "data": {
    "items": [
      {
        "id": "123",
        "name": "深圳华强电子",
        "regStatus": "存续",
        "creditCode": "91440300XXXX",
        "legalPersonName": "张三",
        "registeredCapital": "5000万人民币",
        "estiblishTime": "20100315"
      }
    ]
  }
}
```

天眼查规则：

1. 未配置天眼查 Key 时，不阻断供应商搜索。
2. 企业信息为空时，供应商仍然展示。
3. `credit_score` 可返回 `null`。
4. `risk_level` 可返回 `待确认`。
5. `certifications` 可返回空数组。

---

## 4. 信息架构

```text
采购成本与供应商搜索智能体
├── 顶部 Header
│   ├── 标题
│   ├── Tab：采购成本分析
│   ├── Tab：供应商搜索
│   └── API 设置按钮
├── 采购成本分析页
│   ├── 搜索卡片
│   ├── 数据来源提示
│   ├── 产品列表
│   └── 产品分析/对比 + 采购建议
├── 供应商搜索页
│   ├── 供应商条件表单
│   ├── 搜索来源标签
│   ├── 供应商结果表格/卡片
│   ├── 供应商详情弹窗
│   └── 面谈问题生成器
└── API 设置弹窗
```

### 4.1 主导航

| Tab ID | 名称 | 默认状态 |
|---|---|---|
| `price` | 采购成本分析 | 默认选中 |
| `supplier` | 供应商搜索 | 非默认 |

导航不显示 emoji，不显示英文副标题。

### 4.2 默认页面状态

首次打开：

1. URL：以前端启动日志输出的本地地址为准，例如 `http://localhost:3000` 或 `http://localhost:5173`。
2. 默认进入采购成本分析页。
3. 顶部标题：`采购成本与供应商搜索智能体`
4. 右上角显示 API 设置按钮。
5. 背景为浅色蓝青渐变，有呼吸光斑。

---

## 5. API 设置与配置状态

### 5.1 设置弹窗字段

| 字段 | localStorage 字段 | 用途 |
|---|---|---|
| 百度 AI Studio Access Token | `llmToken` | 采购建议、供应商搜索、面谈问题 |
| 天眼查 API Key | `tianyanchaKey` | 企业资质、信用、风险 |
| Mouser API Key | `mouserApiKey` | 物料价格、库存、交期查询 |

### 5.2 localStorage 存储规范

localStorage 顶层 key 固定为：

```text
jintian_api_keys
```

value 固定为：

```json
{
  "llmToken": "",
  "tianyanchaKey": "",
  "mouserApiKey": ""
}
```

写入时必须使用：

```js
localStorage.setItem('jintian_api_keys', JSON.stringify(apiKeys))
```

读取时必须使用 `JSON.parse`：

```js
function getApiKeys() {
  try {
    const raw = localStorage.getItem('jintian_api_keys')
    return raw
      ? JSON.parse(raw)
      : { llmToken: '', tianyanchaKey: '', mouserApiKey: '' }
  } catch {
    return { llmToken: '', tianyanchaKey: '', mouserApiKey: '' }
  }
}
```

### 5.3 配置状态判断规则

前端界面显示是否配置时，必须合并判断：

```js
const llmConfigured = Boolean(apiKeys.llmToken) || Boolean(health?.llm_configured)
const mouserConfigured = Boolean(apiKeys.mouserApiKey) || Boolean(health?.mouser_configured)
const tianyanchaConfigured = Boolean(apiKeys.tianyanchaKey) || Boolean(health?.tianyancha_configured)
```

禁止只依赖 `/api/health`。

原因：`/api/health` 只能知道后端 `.env`，不知道浏览器 localStorage。

### 5.4 保存后立即更新

保存设置时必须同时更新 localStorage 和 React state：

```js
function handleSave(newKeys) {
  localStorage.setItem('jintian_api_keys', JSON.stringify(newKeys))
  setApiKeys(newKeys)
}
```

否则会出现：保存了 API，但界面仍然显示未配置。

### 5.5 请求头注入

前端每次请求前都必须实时读取 localStorage 并注入 Header：

| Header | 来源 |
|---|---|
| `X-LLM-Token` | `llmToken` |
| `X-Tianyancha-Key` | `tianyanchaKey` |
| `X-Mouser-Key` | `mouserApiKey` |

---

## 6. 前端 API 调用层

文件路径固定：

```text
frontend/src/services/api.js
```

所有请求必须通过此文件，不允许组件里直接写 axios 或 fetch。

```js
import axios from 'axios'

const STORAGE_KEY = 'jintian_api_keys'

function getApiKeys() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw
      ? JSON.parse(raw)
      : { llmToken: '', tianyanchaKey: '', mouserApiKey: '' }
  } catch {
    return { llmToken: '', tianyanchaKey: '', mouserApiKey: '' }
  }
}

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 180000,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.request.use((config) => {
  const keys = getApiKeys()

  if (keys.llmToken) {
    config.headers['X-LLM-Token'] = keys.llmToken
  }

  if (keys.tianyanchaKey) {
    config.headers['X-Tianyancha-Key'] = keys.tianyanchaKey
  }

  if (keys.mouserApiKey) {
    config.headers['X-Mouser-Key'] = keys.mouserApiKey
  }

  return config
})

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message =
      error?.response?.data?.message ||
      error?.response?.data?.detail ||
      error?.message ||
      '请求失败'

    return Promise.reject(new Error(message))
  }
)

export const api = {
  getHealth: () => apiClient.get('/health'),

  searchPrice: (model, options = {}) =>
    apiClient.get('/price/search', {
      params: {
        model,
        include_history: options.includeHistory || false
      }
    }),

  sourcing: (data) =>
    apiClient.post('/supplier/sourcing', data),

  generateInterviewQuestions: (data) =>
    apiClient.post('/supplier/interview-questions', data),

  chat: (message, context = null) =>
    apiClient.post('/chat', {
      message,
      context
    })
}

export default api
```

必须遵守：

1. 响应拦截器必须返回 `response.data`。
2. 组件不能读取 `result.data.products`。
3. 组件必须直接读取 `result.products`、`result.suppliers`、`result.message`。
4. 保存 API 设置后，下一次请求必须自动携带最新 Key。
5. 组件禁止直接调用 `apiClient.get`、`apiClient.post`。

---

## 7. 后端 API 接口

### 7.1 FastAPI 路由

后端入口：

```text
backend/main.py
```

必须注册：

```python
app.include_router(price.router, prefix="/api/price", tags=["价格查询"])
app.include_router(supplier.router, prefix="/api/supplier", tags=["供应商搜索"])
app.include_router(chat.router, prefix="/api/chat", tags=["采购建议"])
```

额外提供：

```text
GET /api/health
```

### 7.2 健康检查

#### GET `/api/health`

响应：

```json
{
  "status": "ok",
  "llm_configured": false,
  "tianyancha_configured": false,
  "mouser_configured": false,
  "version": "1.0.0"
}
```

注意：该接口只反映后端 `.env`，前端必须与 localStorage 合并判断。

### 7.3 价格查询

#### GET `/api/price/search`

参数：

| 参数 | 类型 | 必填 |
|---|---|---|
| `model` | string | 是 |
| `include_history` | boolean | 否 |

响应：

```json
{
  "model": "STM32F103C8T6",
  "platform": "Mouser",
  "products": [],
  "market_overview": {
    "avg_price": null,
    "price_range": [null, null],
    "trend": "平稳"
  },
  "history": [],
  "mouser_configured": true,
  "api_used": "mouser",
  "data_source": "Mouser API (实时数据)",
  "total_found": 0
}
```

### 7.4 采购建议

#### POST `/api/chat`

请求：

```json
{
  "message": "采购建议 prompt 文本",
  "context": null
}
```

响应：

```json
{
  "message": "Markdown 格式采购建议文本"
}
```

### 7.5 供应商搜索

#### POST `/api/supplier/sourcing`

请求：

```json
{
  "material": {
    "model": "RF模块 KBD600 433M",
    "category": "RF模块",
    "spec": "433MHz, 10mW",
    "annual_usage": 1000000,
    "pain_points": ["价格贵", "交期长"],
    "requirements": ["小批量订单", "技术支持"],
    "accept_substitute": true
  },
  "current_supplier": "粤盛",
  "preferred_regions": ["深圳", "东莞"]
}
```

响应：

```json
{
  "material": {
    "model": "RF模块 KBD600 433M",
    "category": "RF模块",
    "spec": "433MHz, 10mW",
    "annual_usage": 1000000,
    "pain_points": ["价格贵", "交期长"],
    "requirements": ["小批量订单", "技术支持"],
    "accept_substitute": true
  },
  "suppliers": [
    {
      "name": "深圳华强电子",
      "region": "广东深圳",
      "category": "芯片/IC",
      "products": ["芯片/IC", "MCU"],
      "advantages": ["原装正品", "交期稳定"],
      "served_clients": [],
      "match_score": 92,
      "certifications": ["ISO9001"],
      "source": "联网搜索",
      "risk_level": "低风险",
      "credit_score": 92
    }
  ],
  "total_found": 1,
  "search_sources": ["联网搜索", "天眼查"],
  "search_details": "",
  "generated_at": "2026-06-12T12:00:00"
}
```

### 7.6 面谈问题生成

#### POST `/api/supplier/interview-questions`

请求：

```json
{
  "suppliers": ["深圳华强电子", "上海贸泽电子"],
  "material": {
    "model": "STM32F103C8T6",
    "category": "芯片/IC",
    "spec": "",
    "annual_usage": 10000,
    "pain_points": ["交期长"],
    "requirements": ["技术支持"],
    "accept_substitute": true
  },
  "focus_areas": ["价格", "交期", "质量"]
}
```

响应：

```json
{
  "questions_by_supplier": {
    "深圳华强电子": [
      {
        "category": "产品与质量",
        "question": "针对 STM32F103C8T6，贵司能否提供原厂授权、质量认证、批次追溯和样品测试资料？",
        "priority": "high",
        "context": "确认产品来源、质量体系和可追溯性"
      }
    ]
  },
  "common_questions": [
    {
      "category": "通用问题",
      "question": "请提供报价有效期、付款条件、交付周期和售后联系人信息。",
      "priority": "medium"
    }
  ],
  "generated_at": "2026-06-12T12:00:00"
}
```

---

## 8. 功能模块详细设计

### 8.1 Header

组件路径：

```text
frontend/src/components/layout/Header.jsx
```

| 元素 | 要求 |
|---|---|
| 标题 | `采购成本与供应商搜索智能体` |
| Tab | `采购成本分析`、`供应商搜索` |
| 默认 Tab | 采购成本分析 |
| 设置按钮 | 右上角，点击打开 API 设置 |
| 设置状态 | LLM 已配置显示绿色，未配置显示灰色 |
| emoji | 不显示 |

### 8.2 API 设置弹窗

组件路径：

```text
frontend/src/components/common/SettingsModal.jsx
```

字段：

1. 百度 AI Studio Access Token
2. 天眼查 API Key
3. Mouser API Key

交互：

| 操作 | 行为 |
|---|---|
| 点击设置按钮 | 打开弹窗 |
| 点击遮罩 | 关闭弹窗 |
| 点击取消 | 关闭弹窗，不保存 |
| 点击保存设置 | 写入 localStorage，更新 state，显示“已保存”，800ms 后关闭 |
| 点击显示/隐藏 | 切换 password/text |

底部提示：

```text
Key 仅存储在本地浏览器
```

### 8.3 采购成本分析页

组件路径：

```text
frontend/src/components/price/PriceTracker.jsx
```

页面结构：

```text
采购成本分析页
├── 搜索卡片
│   ├── 标题：采购成本分析
│   ├── 说明：查看阶梯价、库存与交期，辅助采购判断。
│   ├── 输入框
│   ├── 查询按钮
│   └── 快捷查询按钮组
├── 错误提示
├── 数据来源提示
├── 产品列表
└── 产品分析/对比面板 + 采购建议
```

输入框 placeholder：

```text
输入物料型号，如: STM32F103C8T6, ESP32-WROOM-32, LM7805
```

快捷型号：

```text
STM32F103C8T6、ESP32-WROOM-32、LM7805、ATmega328P
```

查询行为：

1. 用户输入物料型号。
2. 点击“查询”或提交表单。
3. 输入为空时不发请求。
4. 调用 `api.searchPrice(model)`。
5. 查询中按钮显示 `查询中...`。
6. 成功后显示产品列表。
7. 失败后显示错误提示。

产品列表字段：

| 字段 | 数据 |
|---|---|
| 产品图片 | `image_path` |
| 制造商料号 | `manufacturer_part_number` |
| 制造商 | `manufacturer` |
| 描述 | `description` |
| 第一档价格 | `price_breaks[0].price` |
| 库存 | `availability_in_stock` |
| 卷带标签 | `reeling` |

产品分析/对比显示条件：

```js
showCompare === true && selectedProducts.length >= 1
```

标题：

| 选中数量 | 标题 |
|---|---|
| 1 | 产品分析 |
| >1 | 产品对比 |

对比字段：

- 制造商
- 描述
- 价格梯度
- 现货库存
- 在途库存
- MOQ / 倍数
- 交期
- 封装
- 卷带供应
- RoHS
- 替代型号
- 产品链接

采购建议流程：

1. 点击“采购建议”或“对比分析”。
2. 展示对比面板。
3. 构造 prompt。
4. 调用 `api.chat(prompt)`。
5. 使用 `ReactMarkdown` 渲染结果。

加载步骤：

```text
正在整理产品对比数据...
正在分析价格竞争力...
正在评估供货能力与风险...
正在生成采购推荐方案...
```

### 8.4 供应商搜索页

组件路径：

```text
frontend/src/components/supplier/SupplierFinder.jsx
```

页面结构：

```text
供应商搜索页
├── 页面标题卡片
├── 左侧供应商条件表单
├── 右侧搜索结果区
│   ├── 加载状态
│   ├── 搜索来源标签
│   ├── 供应商表格
│   ├── 供应商卡片
│   └── 面谈问题生成器
```

标题：

```text
供应商搜索
搜索供应商，整理资质与面谈问题。
```

### 8.5 供应商条件表单

组件路径：

```text
frontend/src/components/supplier/SourcingForm.jsx
```

字段：

| 字段 | 类型 | 默认值 | 必填 |
|---|---|---|---|
| 物料型号 | 文本 | 空 | 否 |
| 物料类别 | 下拉 | 芯片/IC | 是 |
| 规格参数 | 文本 | 空 | 否 |
| 年用量 | 数字 | 空 | 否 |
| 当前痛点 | 标签多选 + 自定义 | 空 | 否 |
| 采购要求 | 标签多选 + 自定义 | 空 | 否 |
| 当前供应商 | 文本 | 空 | 否 |
| 期望地区 | 标签多选 | 不限 | 否 |

物料类别：

```text
芯片/IC、液晶/显示屏、面板、PCB、被动元件、连接器、RF模块、非标件、其他
```

当前痛点：

```text
价格贵、起订量多、交期长、质量不稳定、保供风险、资质不全、服务差
```

采购要求：

```text
可提供参考规格书、接受替代品牌、小批量订单、账期支持、技术支持、样品测试
```

期望地区：

```text
深圳、上海、东莞、杭州、苏州、南京、北京、成都、不限
```

提交按钮：

| 状态 | 文案 |
|---|---|
| 默认 | 开始搜索 |
| loading | 正在搜索供应商... |

### 8.6 供应商结果区

表格组件路径：

```text
frontend/src/components/supplier/SupplierTable.jsx
```

表头：

| 列 | 说明 |
|---|---|
| 多选框 | 用于选择供应商 |
| 供应商名称 | 名称、风险标签、信用分 |
| 地点 | 可排序 |
| 主要优势 | 最多前 2 个 |
| 可供应产品 | 最多前 2 个 |
| 已服务客户 | 最多前 2 个 |
| 信息来源 | 联网搜索 / 推荐供应商 / 天眼查 |

不显示“匹配度”列。

卡片组件路径：

```text
frontend/src/components/supplier/SupplierCard.jsx
```

卡片展示：

- 名称
- 地区
- 品类
- 产品
- 优势
- 风险
- 信用分
- 来源

点击卡片或详情按钮打开详情弹窗。

### 8.7 面谈问题生成器

组件路径：

```text
frontend/src/components/supplier/InterviewGenerator.jsx
```

显示逻辑：

| 条件 | 显示 |
|---|---|
| 未选择供应商 | 提示先勾选供应商 |
| 已选择供应商 | 显示关注领域和生成按钮 |
| 生成成功 | 显示问题清单 |
| 生成失败 | 显示错误 |

默认关注领域：

```text
价格、交期、质量
```

可选关注领域：

```text
价格、起订量、交期、质量、资质、服务、技术支持
```

生成按钮：

```text
生成 N 家供应商的面谈问题
```

导出文件名：

```text
面谈问题_{material.model || '供应商'}_{YYYY-MM-DD}.txt
```

---

## 9. 数据模型

### 9.1 Product

```json
{
  "mouser_part_number": "string",
  "manufacturer_part_number": "string",
  "manufacturer": "string",
  "description": "string",
  "category": "string",
  "image_path": "string",
  "datasheet_url": "string",
  "product_url": "string",
  "availability_in_stock": 0,
  "availability_on_order": [],
  "factory_stock": 0,
  "price_breaks": [
    {
      "quantity": 1,
      "price": "18.50",
      "currency": "USD"
    }
  ],
  "price": "18.50",
  "currency": "USD",
  "moq": 1,
  "order_multiple": 1,
  "lead_time": "8 Weeks",
  "reeling": false,
  "standard_pack_qty": 90,
  "package": "LQFP-48",
  "rohs_status": "RoHS Compliant",
  "lifecycle_status": "Active",
  "product_compliance": [],
  "suggested_replacement": "",
  "alternate_packagings": []
}
```

### 9.2 Supplier

```json
{
  "name": "string",
  "region": "string",
  "category": "string",
  "products": ["string"],
  "advantages": ["string"],
  "served_clients": ["string"],
  "match_score": 0,
  "certifications": ["string"],
  "source": "string",
  "risk_level": "低风险 | 中风险 | 高风险 | 待确认",
  "credit_score": 92
}
```

### 9.3 InterviewQuestion

```json
{
  "category": "产品与质量",
  "question": "具体问题",
  "priority": "high | medium | low",
  "context": "问题背景"
}
```

---

## 10. Mock 与智能降级策略

本项目允许 Mock 和降级，但必须遵守一个原则：

> 降级数据结构必须与真实数据完全一致，不能导致前端另写一套逻辑。

### 10.1 价格查询降级

| 条件 | 行为 |
|---|---|
| Mouser Key 已配置且成功 | 返回真实 Mouser 数据 |
| Mouser Key 未配置 | 返回 Mock 产品数据 |
| Mouser 调用失败 | 返回错误提示或 Mock 数据，并在 `data_source` 标注 |

Mock 响应中：

```json
{
  "api_used": "mock",
  "data_source": "Mock 数据（演示模式）",
  "mouser_configured": false
}
```

### 10.2 采购建议降级

| 条件 | 行为 |
|---|---|
| LLM Token 已配置且成功 | 返回真实 LLM 建议 |
| LLM Token 未配置 | 返回模板采购建议 |
| LLM 调用失败 | 返回模板采购建议，并提示原因 |

### 10.3 供应商搜索降级

| 条件 | 行为 |
|---|---|
| LLM Token 已配置且成功 | 返回 LLM 供应商搜索结果 |
| LLM 未配置 | 返回内置推荐供应商 |
| LLM 调用失败 | 返回内置推荐供应商，并写入 `search_details` |

### 10.4 面谈问题降级

| 条件 | 行为 |
|---|---|
| LLM Token 已配置且成功 | 返回 LLM 生成问题 |
| LLM 未配置 | 返回模板问题 |
| LLM 调用失败 | 返回模板问题，并显示提示 |

---

## 11. 前端状态机与按钮规范

### 11.1 表单提交

所有表单提交函数第一行必须：

```js
e.preventDefault()
```

示例：

```js
function handleSubmit(e) {
  e.preventDefault()
  // 后续提交逻辑
}
```

### 11.2 非提交按钮

表单内所有非提交按钮必须显式写：

```jsx
<button type="button">
```

包括：

- 痛点标签
- 采购要求标签
- 地区标签
- 添加按钮
- 删除按钮
- 视图切换按钮
- 展开/收起按钮

否则浏览器会默认触发表单提交，导致页面刷新，表现为“点击按钮没有反应”。

### 11.3 组件导出导入

所有组件必须默认导出：

```js
export default function SupplierFinder() {}
```

导入时：

```js
import SupplierFinder from './components/supplier/SupplierFinder'
```

禁止：

```js
import { SupplierFinder } from './components/supplier/SupplierFinder'
```

否则会导致 React 页面白屏。

### 11.4 异步状态

每个请求区域必须包含：

- loading
- error
- empty
- success

---

## 12. 视觉规范

### 12.1 整体风格

| 项 | 要求 |
|---|---|
| 背景 | `from-slate-50 via-blue-50 to-cyan-50` |
| 风格 | 科技感、轻量、玻璃感 |
| 字体 | Inter、PingFang SC、Microsoft YaHei、system-ui |
| 圆角 | 大圆角 |
| 阴影 | soft / glow |
| emoji | 页面标题和导航不使用 emoji |

### 12.2 Tailwind 扩展

`frontend/tailwind.config.js` 必须包含：

```js
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      boxShadow: {
        soft: '0 18px 45px rgba(15, 23, 42, 0.08)',
        glow: '0 12px 34px rgba(37, 99, 235, 0.18), 0 0 24px rgba(6, 182, 212, 0.16)',
        'glow-lg': '0 18px 44px rgba(37, 99, 235, 0.24), 0 0 34px rgba(6, 182, 212, 0.22)'
      },
      keyframes: {
        breath: {
          '0%, 100%': { opacity: '0.55', transform: 'scale(1)' },
          '50%': { opacity: '0.9', transform: 'scale(1.08)' }
        },
        'breath-slow': {
          '0%, 100%': { opacity: '0.45', transform: 'scale(1)' },
          '50%': { opacity: '0.75', transform: 'scale(1.12)' }
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-6px)' }
        }
      },
      animation: {
        breath: 'breath 5.5s ease-in-out infinite',
        'breath-slow': 'breath-slow 8s ease-in-out infinite',
        float: 'float 4.5s ease-in-out infinite'
      }
    }
  },
  plugins: []
}
```

---

## 13. 项目文件结构

```text
procurement-agent/
├── PRD.md
├── backend/
│   ├── .env
│   ├── .env.example
│   ├── pyproject.toml
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── price.py
│   │   ├── supplier.py
│   │   └── chat.py
│   └── services/
│       ├── mouser.py
│       ├── llm.py
│       └── enterprise.py
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── postcss.config.js
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── index.css
        ├── services/
        │   └── api.js
        ├── hooks/
        │   ├── useApi.js
        │   └── useLocalStorage.js
        └── components/
            ├── layout/
            │   └── Header.jsx
            ├── common/
            │   ├── SettingsModal.jsx
            │   └── LoadingSteps.jsx
            ├── price/
            │   └── PriceTracker.jsx
            └── supplier/
                ├── SupplierFinder.jsx
                ├── SourcingForm.jsx
                ├── SupplierTable.jsx
                ├── SupplierCard.jsx
                ├── SupplierDetailModal.jsx
                └── InterviewGenerator.jsx
```

---

## 14. 关键配置文件

### 14.1 frontend/vite.config.js

```js
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendUrl = env.VITE_API_BASE_URL || 'http://localhost:8000'
  const frontendPort = env.VITE_DEV_PORT ? Number(env.VITE_DEV_PORT) : undefined

  return {
    plugins: [react()],
    server: {
      port: frontendPort,
      proxy: {
        '/api': {
          target: backendUrl,
          changeOrigin: true
        }
      }
    }
  }
})
```

说明：

- `VITE_API_BASE_URL` 用于配置后端实际地址，例如 `http://localhost:8000`。
- `VITE_DEV_PORT` 可选，用于指定前端端口；不配置时由 Vite 自动选择可用端口。
- 组件中仍然只能请求 `/api/...`，不能写死后端地址。

### 14.2 backend/config.py

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LLM_ACCESS_TOKEN: str = ""
    LLM_API_URL: str = "https://aistudio.baidu.com"
    LLM_MODEL: str = "ernie-4.5-turbo-128k"

    TIANYANCHA_API_KEY: str = ""
    TIANYANCHA_API_URL: str = "https://open.api.tianyancha.com"

    MOUSER_API_KEY: str = ""
    MOUSER_API_URL: str = "https://api.mouser.com"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"

settings = Settings()
```

### 14.3 backend/.env.example

```env
LLM_ACCESS_TOKEN=
LLM_API_URL=https://aistudio.baidu.com
LLM_MODEL=ernie-4.5-turbo-128k

TIANYANCHA_API_KEY=
TIANYANCHA_API_URL=https://open.api.tianyancha.com

MOUSER_API_KEY=
MOUSER_API_URL=https://api.mouser.com

HOST=0.0.0.0
PORT=8000
```

说明：`PORT=8000` 只是默认示例，如端口被占用，可以改为任意可用端口，例如 `8001`、`9000`。

---

## 15. 启动命令

### 15.1 后端

推荐 uv：

```bash
cd backend
uv venv
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --reload
```

如果当前端口被占用，可以指定其他端口：

```bash
PORT=8001 uv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

如果不用 uv：

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi==0.115.0 uvicorn==0.30.0 httpx==0.27.0 python-dotenv==1.0.1 pydantic==2.9.0 pydantic-settings==2.5.2
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --reload
```

访问：

```text
http://localhost:<后端实际端口>/api/health
```

### 15.2 前端

```bash
cd frontend
npm install
npm run dev
```

访问：

```text
以终端输出的 Local 地址为准，例如 http://localhost:5173
```

如果后端不是 8000 端口，需要在前端 `.env` 中配置：

```env
VITE_API_BASE_URL=http://localhost:<后端实际端口>
```

### 15.3 构建验证

```bash
cd frontend
npm run build
```

---

## 16. 验收标准

### 16.1 全局验收

- [ ] 打开前端本地地址（以终端启动日志为准）不白屏。
- [ ] 默认进入采购成本分析页。
- [ ] 标题为 `采购成本与供应商搜索智能体`。
- [ ] 只有两个 Tab：采购成本分析、供应商搜索。
- [ ] API 设置弹窗可打开、保存、关闭。
- [ ] localStorage 中保存 `jintian_api_keys`。
- [ ] 保存 Key 后 Header 状态立即更新。
- [ ] Network 请求头能看到对应 Key。

### 16.2 采购成本分析验收

- [ ] 输入 `STM32F103C8T6` 可查询。
- [ ] 查询中显示 `查询中...`。
- [ ] 查询成功后显示数据来源。
- [ ] 显示产品列表。
- [ ] 产品卡片可选中。
- [ ] 选 1 个产品显示 `采购建议`。
- [ ] 选多个产品显示 `对比分析`。
- [ ] 点击后显示产品分析/对比面板。
- [ ] 采购建议区域可渲染 Markdown。

### 16.3 供应商搜索验收

- [ ] 供应商页标题为 `供应商搜索`。
- [ ] 左侧表单标题为 `供应商条件`。
- [ ] 痛点、采购要求、地区标签可点击。
- [ ] 点击 `开始搜索` 有 loading。
- [ ] 搜索结果显示供应商数量。
- [ ] 表格不显示匹配度列。
- [ ] 表格和卡片视图可切换。
- [ ] 可勾选供应商。

### 16.4 面谈问题验收

- [ ] 未选择供应商时提示先勾选。
- [ ] 选择供应商后显示关注领域。
- [ ] 默认选中价格、交期、质量。
- [ ] 点击生成后显示问题清单。
- [ ] 每条问题包含类别、优先级、问题、背景。
- [ ] 可复制单条问题。
- [ ] 可导出 txt。

---

## 17. 开发避坑指南

### 17.1 API 配置了但显示未配置

原因：

- 只读取 `/api/health`，没有读取 localStorage。

正确做法：

```js
const llmConfigured = Boolean(apiKeys.llmToken) || Boolean(health?.llm_configured)
```

### 17.2 保存设置后请求没带 Key

原因：

- axios 拦截器只在初始化时读取了一次 localStorage。

正确做法：

- 每次请求前都调用 `getApiKeys()`。

### 17.3 Token 带引号导致认证失败

原因：

- localStorage 存储时用了 `JSON.stringify`，读取时没 `JSON.parse`。

正确做法：

```js
JSON.parse(localStorage.getItem('jintian_api_keys'))
```

### 17.4 前端页面白屏

常见原因：

```js
import { SupplierFinder } from './SupplierFinder'
```

但组件是：

```js
export default function SupplierFinder() {}
```

正确：

```js
import SupplierFinder from './SupplierFinder'
```

### 17.5 点击按钮没有反应

常见原因：

1. 表单提交函数没有 `e.preventDefault()`。
2. `<form>` 内的非提交按钮没写 `type="button"`。
3. loading/error 状态没有渲染。
4. API 响应结构和组件读取字段不一致。

### 17.6 请求成功但页面没有数据

原因：axios 返回了完整 response：

```js
return response
```

组件读的是：

```js
result.products
```

正确：

```js
return response.data
```

### 17.7 百度 AI Studio 调用失败

检查：

- endpoint 是否为 `/llm/lmapi/v3/chat/completions`
- 是否使用 `Authorization: Bearer <token>`
- 是否使用 `max_completion_tokens`
- 是否 `stream: false`

### 17.8 Mouser 调用失败

检查：

- 是否 POST。
- 是否使用 `/api/v1/search/keyword?apiKey=<key>`。
- 是否把 Key 放在 query param。
- 是否读取 `SearchResults.Parts`。
- 是否把原始响应映射为统一 Product 模型。

---

## 18. 不需要实现的功能

以下功能不属于本次复刻范围，AI 不要实现：

1. 用户登录注册。
2. 多用户权限。
3. 后台管理系统。
4. 审批流。
5. 订单管理。
6. 支付功能。
7. 文件上传。
8. OCR。
9. PDF 解析。
10. Docker 部署。
11. 云数据库。
12. 消息通知。
13. 浏览器插件。
14. 移动 App。
15. 复杂多 Agent 编排。

---

## 19. 给 AI 的实现顺序

### Phase 1：项目骨架

1. 创建 `backend/` 和 `frontend/`。
2. 实现 FastAPI 后端启动。
3. 实现 Vite React 前端启动。
4. 配置 Vite `/api` 代理。
5. 实现 `/api/health`。
6. 前端能请求 `/api/health`。

### Phase 2：API 设置

1. 实现 SettingsModal。
2. 保存到 localStorage。
3. App 中维护 `apiKeys` 状态。
4. Header 根据配置状态变色。
5. axios 拦截器注入 Header。

### Phase 3：采购成本分析

1. 实现 `/api/price/search`。
2. 封装 Mouser 服务。
3. 实现 Mock 产品数据。
4. 实现 PriceTracker。
5. 实现产品选择和对比。
6. 实现 `/api/chat`。
7. 渲染采购建议。

### Phase 4：供应商搜索

1. 实现 SourcingForm。
2. 实现 `/api/supplier/sourcing`。
3. 封装 LLM 供应商搜索。
4. 实现内置推荐供应商降级。
5. 实现 SupplierTable / SupplierCard / DetailModal。

### Phase 5：面谈问题

1. 实现 `/api/supplier/interview-questions`。
2. 实现 LLM 问题生成。
3. 实现模板问题降级。
4. 实现分组展示、复制、导出。

### Phase 6：验收

1. 后端启动。
2. 前端启动。
3. 无 Key 模式跑通。
4. 有 Key 模式验证 Header。
5. `npm run build` 通过。

---

## 20. 最终目标

最终交付物必须满足：

1. 前端可访问。
2. 后端可访问。
3. API 设置可保存。
4. 保存后配置状态准确。
5. 采购成本分析可跑通。
6. 供应商搜索可跑通。
7. 面谈问题生成可跑通。
8. Mock/降级不破坏真实功能。
9. 页面不白屏。
10. 按钮点击都有反馈。
11. 构建成功。
12. 技术架构与本 PRD 一致。
