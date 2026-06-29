# API Spec — 外部 API 集成规范

## 1. 百度 AI Studio LLM API

### 1.1 基本信息

| 项目 | 值 |
|------|-----|
| Base URL | `https://aistudio.baidu.com` |
| Chat 端点 | `POST /llm/lmapi/v3/chat/completions` |
| 认证方式 | `Authorization: Bearer <access_token>` |
| Token 获取 | https://aistudio.baidu.com/account/accessToken |

### 1.2 请求格式

```json
{
  "model": "ernie-4.5-turbo-128k",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "temperature": 0.0,
  "max_completion_tokens": 4096,
  "stream": false,
  "web_search": {"enable": true}
}
```

### 1.3 响应格式

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "ernie-4.5-turbo-128k",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 500,
    "total_tokens": 600
  }
}
```

### 1.4 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 401 Unauthorized | Token 无效或过期 | 重新获取 Token |
| 429 Too Many Requests | 请求频率超限 | 降低请求频率或升级配额 |
| 500 Internal Server Error | 服务端错误 | 重试请求 |

---

## 2. 天眼查 API（企业查询）

### 2.1 基本信息

| 项目 | 值 |
|------|-----|
| Base URL | `https://open.api.tianyancha.com` |
| 认证方式 | `Authorization: <api_key>` |
| 文档地址 | https://open.tianyancha.com |

### 2.2 主要端点

#### 搜索企业

```
GET /services/v3/search/searchCompany
Query Params: keyword, pageSize, pageNum
Headers: Authorization: <api_key>
```

#### 企业详情

```
GET /services/v3/company/baseinfo/{company_id}
Headers: Authorization: <api_key>
```

### 2.3 响应示例

```json
{
  "state": "ok",
  "message": "",
  "data": {
    "companyList": [
      {
        "id": 123456789,
        "name": "深圳华强电子有限公司",
        "regStatus": "存续",
        "regCapital": "5000万元人民币",
        "legalPersonName": "张伟",
        "province": "广东",
        "city": "深圳"
      }
    ]
  }
}
```

### 2.4 降级策略

天眼查 API 失败时，使用本地供应商数据库或 Mock 数据。

---

## 3. 立创商城 API（电商价格）

### 3.1 说明

立创商城 API 需要商务合作授权，个人开发者暂无法直接接入。

### 3.2 替代方案

| 方案 | 说明 |
|------|------|
| 网页爬虫 | 抓取立创商城页面数据（注意合规性） |
| 用户输入 | 由用户手动输入价格数据 |
| Mock 数据 | 使用模拟数据演示功能 |

### 3.3 数据结构

```json
{
  "model": "STM32F103C8T6",
  "name": "STM32F103C8T6 单片机",
  "brand": "ST(意法半导体)",
  "price": 6.80,
  "currency": "CNY",
  "stock": 5000,
  "moq": 1,
  "leadTime": 3,
  "productUrl": "https://item.szlcsc.com/xxx"
}
```

---

## 4. 得捷 DigiKey API

### 4.1 基本信息

| 项目 | 值 |
|------|-----|
| Base URL | `https://api.digikey.com` |
| 文档地址 | https://developer.digikey.com |
| 认证方式 | OAuth 2.0 |

### 4.2 主要端点

```
GET /Search/v3/Products/{keyword}
GET /ProductDetail/v3/Products/{productId}
```

---

## 5. 贸泽 Mouser API

### 5.1 基本信息

| 项目 | 值 |
|------|-----|
| Base URL | `https://api.mouser.com/api/v1` |
| 文档地址 | https://www.mouser.com/api |
| 认证方式 | API Key |

---

## 6. 后端代理实现

### 6.1 API 代理模式

```python
# backend/services/llm.py

import httpx
from config import settings

class LLMService:
    def __init__(self, token: str = None):
        self.token = token or settings.LLM_ACCESS_TOKEN
        self.base_url = settings.LLM_API_URL
    
    async def chat_completion(
        self,
        messages: list,
        model: str = "ernie-4.5-turbo-128k",
        temperature: float = 0.0,
        max_tokens: int = 4096,
        enable_web_search: bool = False,
        timeout: float = 180.0
    ) -> str:
        """调用百度 AI Studio LLM API"""
        
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
```

### 6.2 API Key 优先级

```python
def get_effective_key(header_key: str, env_key: str) -> str:
    """获取有效的 API Key"""
    return header_key or env_key
```

---

## 7. 错误处理

### 7.1 统一错误响应

```python
from fastapi import HTTPException
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    code: str
    message: str
    detail: str = None

# 使用示例
raise HTTPException(
    status_code=400,
    detail=ErrorResponse(
        code="INVALID_API_KEY",
        message="API Key 无效",
        detail="请检查 API Key 是否正确"
    ).model_dump()
)
```

### 7.2 重试策略

```python
import asyncio
from functools import wraps

def retry(max_retries: int = 3, delay: float = 1.0):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for i in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if i < max_retries - 1:
                        await asyncio.sleep(delay * (i + 1))
            raise last_error
        return wrapper
    return decorator
```
