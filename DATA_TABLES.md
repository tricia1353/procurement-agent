# 数据表结构说明

本文档定义采购智能体中使用的两张核心数据表：目标物料/寻源需求表 和 现有供应商盘点表。

---

## 一、目标物料/寻源需求表

用于记录需要寻源的物料信息，帮助智能体生成针对性的寻源策略。

### 1. 数据字段定义

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| **物料类别** | 枚举 | ✅ | 物料所属大类 | 芯片/IC、液晶/面板、PCB、被动元件、连接器、其他 |
| **物料名称** | 文本 | ✅ | 物料的中文名称 | 单片机、WiFi模块、液晶屏 |
| **型号规格** | 文本 | ✅ | 完整型号 | STM32F103C8T6、ESP32-WROOM-32、LCD-4.3-480x272 |
| **当前供应商** | 文本 | ⭕ | 当前合作的供应商 | 深圳华强电子 |
| **当前痛点** | 多选 | ⭕ | 当前供应商存在的问题 | 价格高、交期长、质量不稳定、服务差、支持不足 |
| **月用量** | 数字 | ⭕ | 每月采购数量 | 500 |
| **年用量** | 数字 | ⭕ | 每年采购数量 | 6000 |
| **关键采购要求** | 多选 | ⭕ | 必须满足的要求 | 原装正品、交期≤7天、可开票、技术支持 |
| **是否接受替代品牌** | 布尔 | ⭕ | 是否可接受其他品牌替代 | true/false |
| **希望寻找的供应商方向** | 多选 | ⭕ | 期望的供应商特征 | 国产替代、规模适中、性价比高、技术支持强 |

### 2. 痛点选项列表

```javascript
const painPoints = [
  { id: 'high_price', label: '价格偏高' },
  { id: 'long_lead_time', label: '交期过长' },
  { id: 'quality_issue', label: '质量不稳定' },
  { id: 'poor_service', label: '服务响应差' },
  { id: 'no_support', label: '技术支持不足' },
  { id: 'stock_shortage', label: '经常缺货' },
  { id: 'payment_strict', label: '付款条件苛刻' },
  { id: 'other', label: '其他' }
]
```

### 3. 关键采购要求选项列表

```javascript
const requirements = [
  { id: 'original', label: '原装正品' },
  { id: 'quick_delivery', label: '交期短（≤7天）' },
  { id: 'invoice', label: '可开具发票' },
  { id: 'tech_support', label: '有技术支持' },
  { id: 'samples', label: '提供样品' },
  { id: 'warranty', label: '有质保' },
  { id: 'iso_certified', label: 'ISO认证' }
]
```

### 4. 供应商方向选项列表

```javascript
const supplierDirections = [
  { id: 'domestic', label: '国产替代' },
  { id: 'medium_size', label: '规模适中' },
  { id: 'cost_effective', label: '性价比高' },
  { id: 'tech_strong', label: '技术支持强' },
  { id: 'authorized', label: '授权代理商' },
  { id: 'nearby', label: '本地区域' },
  { id: 'reliable', label: '长期稳定' }
]
```

### 5. JSON 示例

```json
{
  "category": "芯片",
  "name": "ARM Cortex-M 单片机",
  "model": "STM32F103C8T6",
  "current_supplier": "深圳华强电子",
  "pain_points": ["价格偏高", "交期较长"],
  "monthly_usage": 500,
  "annual_usage": 6000,
  "requirements": ["原装正品", "交期短（≤7天）"],
  "accept_substitute": true,
  "supplier_directions": ["国产替代", "性价比高"]
}
```

---

## 二、现有供应商盘点表

用于记录现有供应商信息，帮助智能体进行供应商评估和补充/替换决策。

### 1. 数据字段定义

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| **供应商名称** | 文本 | ✅ | 企业全称 | 深圳华强电子有限公司 |
| **主要供应品类** | 文本 | ✅ | 主要产品类型 | 芯片/IC、电子元器件 |
| **所在地区** | 文本 | ✅ | 企业注册地 | 广东深圳 |
| **来源方式** | 枚举 | ⭕ | 与该供应商的合作来源 | 熟人推荐、客户指定、老供应商、网络搜索、自主开发、展会认识、客户推荐 |
| **推荐原因** | 文本 | ⭕ | 最初选择该供应商的原因 | 品牌授权、价格优势、他人介绍、展会认识 |
| **合作年限** | 整数 | ⭕ | 已合作年数 | 5 |
| **主要优势** | 文本数组 | ⭕ | 该供应商的核心优势 | 原装正品、交期稳定、技术支持好、现货库存、BOM配单 |
| **主要问题** | 文本数组 | ⭕ | 该供应商的不足 | 价格偏高、最小起订量大、部分型号缺货 |
| **是否希望补充或替换** | 枚举 | ⭕ | 是否需要找替代 | 保持、补充、替换 |

### 2. 来源方式选项列表

```javascript
const sourceTypes = [
  { id: 'referral', label: '熟人推荐' },
  { id: 'customer_specified', label: '客户指定' },
  { id: 'old_supplier', label: '老供应商' },
  { id: 'web_search', label: '网络搜索' },
  { id: 'self_developed', label: '自主开发' },
  { id: 'exhibition', label: '展会认识' },
  { id: 'customer_referral', label: '客户推荐' }
]
```

### 3. 替换/补充决策选项

```javascript
const replacementOptions = [
  { id: 'keep', label: '保持' },
  { id: 'supplement', label: '补充（增加备选）' },
  { id: 'replace', label: '替换（寻找替代）' }
]
```

### 4. JSON 示例

```json
{
  "name": "深圳华强电子有限公司",
  "category": "芯片/IC",
  "region": "广东深圳",
  "source_type": "熟人推荐",
  "referral_reason": "品牌授权代理",
  "cooperation_years": 5,
  "advantages": ["原装正品", "交期稳定", "技术支持好"],
  "issues": ["价格偏高", "最小起订量大"],
  "replacement_decision": "supplement"
}
```

---

## 三、使用场景

### 场景 1：寻源需求表的应用

当需要为新物料寻找供应商时：

1. 填写【目标物料/寻源需求表】
2. 智能体根据表中的"物料类别"、"型号"、"关键要求"进行寻源
3. 如果"接受替代品牌"为 true，智能体会推荐国产替代方案
4. 结合"供应商方向"筛选推荐结果

### 场景 2：供应商盘点表的应用

当评估现有供应商时：

1. 查看【现有供应商盘点表】
2. 根据"合作年限"、"主要优势"、"主要问题"进行评估
3. 根据是否需要"补充或替换"制定供应商优化策略
4. 结合天眼查等企业信息验证供应商资质

---

## 四、数据存储建议

### 存储方式

| 数据 | 推荐存储方式 |
|------|-------------|
| 物料需求表 | SQLite + 本地缓存（物料级别） |
| 供应商盘点表 | SQLite + 本地缓存（供应商级别） |
| 价格历史 | SQLite（按型号+平台+日期索引） |

### 数据结构（SQLite）

```sql
-- 物料需求表
CREATE TABLE material_requirements (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  category TEXT NOT NULL,
  name TEXT NOT NULL,
  model TEXT NOT NULL,
  current_supplier TEXT,
  pain_points TEXT,  -- JSON 数组
  monthly_usage INTEGER,
  annual_usage INTEGER,
  requirements TEXT,  -- JSON 数组
  accept_substitute BOOLEAN DEFAULT 0,
  supplier_directions TEXT,  -- JSON 数组
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_material_model ON material_requirements(model);

-- 供应商盘点表
CREATE TABLE supplier_inventory (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  category TEXT,
  region TEXT,
  source_type TEXT,
  referral_reason TEXT,
  cooperation_years INTEGER,
  advantages TEXT,  -- JSON 数组
  issues TEXT,  -- JSON 数组
  replacement_decision TEXT,
  credit_score INTEGER,
  risk_level TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_supplier_region ON supplier_inventory(region);
CREATE INDEX idx_supplier_category ON supplier_inventory(category);
```

---

## 五、与智能体的关联

### 价格追踪 + 寻源需求表

当用户查询某个物料时，智能体会：
1. 检查该物料是否在【寻源需求表】中
2. 如果在表中，优先推荐满足"关键采购要求"的供应商
3. 根据"是否接受替代品牌"决定是否展示替代型号

### 供应商寻源 + 供应商盘点表

当用户搜索供应商时，智能体会：
1. 检查搜索结果中的供应商是否在【盘点表】中
2. 显示合作年限、历史评价等上下文信息
3. 根据"是否需要补充或替换"决定是否标注"建议替代"标签

### 报价分析 + 两张表的结合

当分析报价时，智能体会：
1. 参考【寻源需求表】中的"关键采购要求"作为评分维度
2. 检查报价供应商是否在【盘点表】中
3. 结合"主要优势"和"主要问题"给出采购建议