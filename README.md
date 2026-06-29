采购智能体 Demo
===============

基于 Claude API + Web搜索 + 企业查询 + 电商搜索的采购辅助系统

## 功能模块

### 1. 价格追踪模块
- 芯片/液晶/PCB等电子物料价格查询
- 历史价格趋势分析
- 多平台比价

### 2. 供应商寻源模块
- 基于物料需求推荐供应商
- 企业信息查询（资质、信用、地区）
- 供应商画像生成

### 3. 报价分析模块
- 解析报价单（PDF/Excel）
- 多维度比价分析
- 自动生成比价报告

### 4. 议价助手模块
- 生成议价依据
- 市场行情对比
- 谈判话术建议

## 技术栈

- **大模型**: Claude API (Anthropic)
- **Web搜索**: Bing Search API / 自定义爬虫
- **企业查询**: 模拟企业信息API（可对接天眼查/企查查）
- **电商数据**: 模拟电商API（可对接立创商城/得捷/贸泽）
- **数据存储**: SQLite (本地缓存) + JSON (配置)
- **前端**: Streamlit (快速原型)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

创建 `.env` 文件：

```env
ANTHROPIC_API_KEY=your_anthropic_api_key
BING_SEARCH_API_KEY=your_bing_api_key  # 可选，用于联网搜索
```

### 3. 运行应用

```bash
python main.py
```

或者启动 Streamlit 界面：

```bash
streamlit run app.py
```

## 目录结构

```
procurement-agent/
├── agent/
│   ├── __init__.py
│   ├── core.py           # 智能体核心
│   ├── price_tracker.py  # 价格追踪
│   ├── supplier_finder.py # 供应商寻源
│   ├── quote_analyzer.py # 报价分析
│   └── negotiator.py     # 议价助手
├── api/
│   ├── __init__.py
│   ├── enterprise.py     # 企业查询API
│   ├── ecommerce.py      # 电商API
│   └── search.py         # 网络搜索
├── data/
│   ├── cache.db          # SQLite缓存
│   └── suppliers.json    # 供应商数据库
├── tests/
│   └── test_*.py
├── main.py               # CLI入口
├── app.py                # Streamlit界面
├── requirements.txt
├── .env.example
└── README.md
```

## 使用示例

### CLI 模式

```bash
# 查询芯片价格
python main.py query-price --model "STM32F103C8T6"

# 寻找供应商
python main.py find-suppliers --material "ESP32-WROOM-32" --region "深圳"

# 分析报价
python main.py analyze-quote --quote quotes/supplier_a.xlsx

# 生成议价建议
python main.py negotiate --material "STM32F103C8T6" --target-price 6.0
```

### Web 界面

访问 http://localhost:8501 使用交互式界面。

## 未来扩展

- [ ] 接入真实企业查询API（天眼查/企查查）
- [ ] 接入真实电商平台API（立创商城/得捷/贸泽）
- [ ] 集成企业内部ERP/采购系统
- [ ] 价格预警推送（微信/邮件）
- [ ] 供应商评级系统
- [ ] 多语言支持

## License

MIT License