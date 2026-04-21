# API接口业务文档

## 1. 文档概述

本文档描述了API自动化测试平台的测试接口，用于验证平台功能的正常运行。文档包含了多个常见的HTTP请求接口，涵盖了GET、POST、PUT、DELETE等常见请求方法。

## 2. 测试环境

- **基础URL**: `https://httpbin.org`
- **请求协议**: HTTPS
- **响应格式**: JSON

## 3. 接口列表

| 接口名称 | 接口路径 | 请求方法 | 功能描述 |
|---------|---------|---------|----------|
| 获取用户信息 | /get | GET | 获取用户信息，返回请求参数和头部信息 |
| 创建用户 | /post | POST | 创建用户，返回请求体和头部信息 |
| 更新用户 | /put | PUT | 更新用户信息，返回请求体和头部信息 |
| 删除用户 | /delete | DELETE | 删除用户，返回请求体和头部信息 |
| 状态码测试 | /status/{code} | GET | 返回指定的HTTP状态码 |
| 延迟响应 | /delay/{seconds} | GET | 延迟指定秒数后返回响应 |

## 4. 详细接口说明

### 4.1 获取用户信息接口

- **接口路径**: `/get`
- **请求方法**: `GET`
- **请求头**:
  ```json
  {
    "Content-Type": "application/json",
    "Authorization": "Bearer {token}"
  }
  ```
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |-------|------|------|------|
  | name | string | 否 | 用户名 |
  | age | integer | 否 | 用户年龄 |
- **响应格式**:
  ```json
  {
    "args": {
      "name": "test",
      "age": "25"
    },
    "headers": {
      "Accept": "*/*",
      "Authorization": "Bearer {token}",
      "Content-Type": "application/json",
      "Host": "httpbin.org",
      "User-Agent": "python-requests/2.32.5"
    },
    "origin": "127.0.0.1",
    "url": "https://httpbin.org/get?name=test&age=25"
  }
  ```

### 4.2 创建用户接口

- **接口路径**: `/post`
- **请求方法**: `POST`
- **请求头**:
  ```json
  {
    "Content-Type": "application/json"
  }
  ```
- **请求体**:
  ```json
  {
    "username": "admin",
    "password": "123456",
    "email": "admin@example.com"
  }
  ```
- **响应格式**:
  ```json
  {
    "args": {},
    "data": "{\"username\": \"admin\", \"password\": \"123456\", \"email\": \"admin@example.com\"}",
    "files": {},
    "form": {},
    "headers": {
      "Accept": "*/*",
      "Content-Length": "69",
      "Content-Type": "application/json",
      "Host": "httpbin.org",
      "User-Agent": "python-requests/2.32.5"
    },
    "json": {
      "username": "admin",
      "password": "123456",
      "email": "admin@example.com"
    },
    "origin": "127.0.0.1",
    "url": "https://httpbin.org/post"
  }
  ```

### 4.3 更新用户接口

- **接口路径**: `/put`
- **请求方法**: `PUT`
- **请求头**:
  ```json
  {
    "Content-Type": "application/json"
  }
  ```
- **请求体**:
  ```json
  {
    "id": 1,
    "username": "updated_user",
    "email": "updated@example.com"
  }
  ```
- **响应格式**:
  ```json
  {
    "args": {},
    "data": "{\"id\": 1, \"username\": \"updated_user\", \"email\": \"updated@example.com\"}",
    "files": {},
    "form": {},
    "headers": {
      "Accept": "*/*",
      "Content-Length": "63",
      "Content-Type": "application/json",
      "Host": "httpbin.org",
      "User-Agent": "python-requests/2.32.5"
    },
    "json": {
      "id": 1,
      "username": "updated_user",
      "email": "updated@example.com"
    },
    "origin": "127.0.0.1",
    "url": "https://httpbin.org/put"
  }
  ```

### 4.4 删除用户接口

- **接口路径**: `/delete`
- **请求方法**: `DELETE`
- **请求头**:
  ```json
  {
    "Content-Type": "application/json"
  }
  ```
- **请求体**:
  ```json
  {
    "id": 1
  }
  ```
- **响应格式**:
  ```json
  {
    "args": {},
    "data": "{\"id\": 1}",
    "files": {},
    "form": {},
    "headers": {
      "Accept": "*/*",
      "Content-Length": "13",
      "Content-Type": "application/json",
      "Host": "httpbin.org",
      "User-Agent": "python-requests/2.32.5"
    },
    "json": {
      "id": 1
    },
    "origin": "127.0.0.1",
    "url": "https://httpbin.org/delete"
  }
  ```

### 4.5 状态码测试接口

- **接口路径**: `/status/{code}`
- **请求方法**: `GET`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |-------|------|------|------|
  | code | integer | 是 | HTTP状态码 |
- **响应格式**:
  - 状态码: {code}
  - 响应体: 无

### 4.6 延迟响应接口

- **接口路径**: `/delay/{seconds}`
- **请求方法**: `GET`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |-------|------|------|------|
  | seconds | integer | 是 | 延迟秒数 |
- **响应格式**:
  ```json
  {
    "args": {},
    "data": "",
    "files": {},
    "form": {},
    "headers": {
      "Accept": "*/*",
      "Host": "httpbin.org",
      "User-Agent": "python-requests/2.32.5"
    },
    "origin": "127.0.0.1",
    "url": "https://httpbin.org/delay/3"
  }
  ```

## 5. 测试示例

### 5.1 快速测试示例

1. **测试GET接口**:
   - 基础URL: `https://httpbin.org`
   - 接口路径: `/get`
   - 请求方法: `GET`
   - 请求头: `{"Content-Type": "application/json"}`
   - 请求参数: `?name=test&age=25`

2. **测试POST接口**:
   - 基础URL: `https://httpbin.org`
   - 接口路径: `/post`
   - 请求方法: `POST`
   - 请求头: `{"Content-Type": "application/json"}`
   - 请求体: `{"username": "admin", "password": "123456"}`

### 5.2 测试人员专用示例

使用以下接口文档生成测试用例:

```
# 用户管理接口
- 接口路径: /get
- 请求方法: GET
- 请求头: {"Content-Type": "application/json"}
- 请求参数: {"name": "string", "age": "integer"}
- 响应: {"args": {}, "headers": {}, "origin": "string", "url": "string"}

# 用户创建接口
- 接口路径: /post
- 请求方法: POST
- 请求头: {"Content-Type": "application/json"}
- 请求体: {"username": "string", "password": "string", "email": "string"}
- 响应: {"args": {}, "data": "string", "json": {}, "origin": "string", "url": "string"}

# 用户更新接口
- 接口路径: /put
- 请求方法: PUT
- 请求头: {"Content-Type": "application/json"}
- 请求体: {"id": "integer", "username": "string", "email": "string"}
- 响应: {"args": {}, "data": "string", "json": {}, "origin": "string", "url": "string"}

# 用户删除接口
- 接口路径: /delete
- 请求方法: DELETE
- 请求头: {"Content-Type": "application/json"}
- 请求体: {"id": "integer"}
- 响应: {"args": {}, "data": "string", "json": {}, "origin": "string", "url": "string"}
```

## 6. 错误处理

| 错误码 | 描述 | 解决方案 |
|-------|------|----------|
| 400 | 请求参数错误 | 检查请求参数格式是否正确 |
| 401 | 未授权 | 检查认证信息是否正确 |
| 404 | 接口不存在 | 检查接口路径是否正确 |
| 500 | 服务器内部错误 | 联系开发人员 |

## 7. 注意事项

1. 所有接口均使用HTTPS协议
2. 接口响应时间一般不超过3秒
3. 测试时请使用有效的请求参数
4. 对于需要认证的接口，请提供有效的认证信息

## 8. 变更历史

| 版本 | 变更内容 | 变更时间 |
|------|----------|----------|
| 1.0 | 初始版本 | 2026-04-16 |