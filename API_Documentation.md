# 八字生肖分析API接口文档

## 概述

本API服务提供八字分析和生肖分析功能，基于传统中国命理学原理。

**服务地址**: `http://localhost:5000`

## 接口列表

### 1. 健康检查接口

**请求**:
```
GET /health
```

**响应**:
```json
{
    "status": "healthy"
}
```

### 2. API文档接口

**请求**:
```
GET /
```

**响应**:
```json
{
    "message": "八字生肖分析API服务",
    "endpoints": {
        "/api/shengxiao": "生肖分析 (POST)",
        "/api/bazi": "八字分析 (POST)",
        "/health": "健康检查 (GET)"
    }
}
```

## 核心功能接口

### 3. 生肖分析接口

分析生肖的相合、相冲等关系。

**请求**:
```
POST /api/shengxiao
Content-Type: application/json
```

**请求参数**:
```json
{
    "shengxiao": "鼠"
}
```

**参数说明**:
- `shengxiao` (必填): 生肖名称，有效值为: "鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"

**成功响应** (200):
```json
{
    "shengxiao": "鼠",
    "year_zhi": "子",
    "compatible": {
        "sanhe": ["猴", "龙"],
        "liuhe": ["牛"],
        "sanhui": ["猪", "牛"]
    },
    "incompatible": {
        "chong": ["马"],
        "xing": ["兔"],
        "beixing": ["兔"],
        "hai": ["羊"],
        "po": ["鸡"]
    }
}
```

**错误响应** (400):
```json
{
    "error": "请输入正确的生肖",
    "valid_shengxiaos": ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
}
```

### 4. 八字分析接口

基于出生时间进行详细的八字命理分析。

**请求**:
```
POST /api/bazi
Content-Type: application/json
```

**请求参数**:
```json
{
    "birth_date": "1990-01-01",
    "birth_time": "8",
    "gender": "男"
}
```

**参数说明**:
- `birth_date` (必填): 出生日期，格式为 "YYYY-MM-DD"
- `birth_time` (可选): 出生时辰，0-23的数字字符串，默认为 "8"
- `gender` (可选): 性别，"男" 或 "女"，默认为 "男"

**成功响应** (200):
```json
{
    "birth_info": {
        "date": "1990-01-01",
        "time": "8",
        "gender": "男"
    },
    "analysis": "详细的八字分析文本内容...",
    "success": true
}
```

**错误响应**:

日期格式错误 (400):
```json
{
    "error": "日期格式不正确，请使用 YYYY-MM-DD 格式"
}
```

时辰格式错误 (400):
```json
{
    "error": "时辰格式不正确，请使用 0-23 的整数"
}
```

性别错误 (400):
```json
{
    "error": "性别必须是 '男' 或 '女'"
}
```

服务器错误 (500):
```json
{
    "error": "服务器错误: 具体错误信息",
    "birth_info": {
        "date": "1990-01-01",
        "time": "8",
        "gender": "男"
    }
}
```

## 请求示例

### cURL示例

**生肖分析**:
```bash
curl -X POST http://localhost:5000/api/shengxiao \
  -H "Content-Type: application/json" \
  -d '{"shengxiao": "龙"}'
```

**八字分析（完整参数）**:
```bash
curl -X POST http://localhost:5000/api/bazi \
  -H "Content-Type: application/json" \
  -d '{"birth_date": "1990-01-01", "birth_time": "14", "gender": "女"}'
```

**八字分析（最简参数）**:
```bash
curl -X POST http://localhost:5000/api/bazi \
  -H "Content-Type: application/json" \
  -d '{"birth_date": "1990-01-01"}'
```

### Python示例

```python
import requests
import json

# 生肖分析
response = requests.post(
    'http://localhost:5000/api/shengxiao',
    json={'shengxiao': '龙'},
    headers={'Content-Type': 'application/json'}
)
print(json.dumps(response.json(), ensure_ascii=False, indent=2))

# 八字分析
response = requests.post(
    'http://localhost:5000/api/bazi',
    json={
        'birth_date': '1990-01-01',
        'birth_time': '8',
        'gender': '男'
    },
    headers={'Content-Type': 'application/json'}
)
result = response.json()
print(f"出生信息: {result['birth_info']}")
print(f"分析结果: {result['analysis']}")
```

### JavaScript示例

```javascript
// 生肖分析
fetch('http://localhost:5000/api/shengxiao', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        shengxiao: '龙'
    })
})
.then(response => response.json())
.then(data => console.log(data));

// 八字分析
fetch('http://localhost:5000/api/bazi', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        birth_date: '1990-01-01',
        birth_time: '8',
        gender: '男'
    })
})
.then(response => response.json())
.then(data => {
    console.log('出生信息:', data.birth_info);
    console.log('分析结果:', data.analysis);
});
```

## 启动服务

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 启动服务:
```bash
python api_server.py
```

3. 服务将在 `http://localhost:5000` 启动

## 注意事项

1. **编码**: 所有请求和响应均使用UTF-8编码
2. **时区**: 默认使用本地时区
3. **缓存**: 服务不缓存结果，每次请求都会重新计算
4. **并发**: 服务支持并发请求
5. **日志**: 服务运行时会输出请求日志

## 错误处理

- 400: 客户端请求错误（参数格式错误、缺少必填参数等）
- 500: 服务器内部错误（依赖缺失、脚本执行失败等）

## 版本信息

- API版本: 1.0
- 更新时间: 2024年
- 基于: 传统八字命理学和十二生肖理论