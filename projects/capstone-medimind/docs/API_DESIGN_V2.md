# MediMind 第二期 - API 设计文档

> 版本: v2.0  
> 基础路径: `/api/v1`

---

## 1. 用户认证 API

### POST /auth/register

用户注册。

**请求**:

```json
{
  "email": "user@example.com",
  "password": "password123",
  "nickname": "用户昵称"
}
```

**响应**:

```json
{
  "code": 200,
  "data": {
    "access_token": "eyJhbG...",
    "token_type": "bearer",
    "expires_in": 604800,
    "user": {
      "id": "user_xxxx",
      "email": "user@example.com",
      "nickname": "用户昵称"
    }
  }
}
```

---

### POST /auth/login

用户登录。

**请求**:

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

---

### POST /auth/logout

用户登出。需要 Bearer Token。

---

### GET /auth/me

获取当前用户信息。需要 Bearer Token。

---

### PUT /auth/me

更新用户信息。

**请求**:

```json
{
  "nickname": "新昵称",
  "avatar_url": "https://..."
}
```

---

## 2. 健康档案 API

### GET /profile

获取健康档案。

**响应**:

```json
{
  "code": 200,
  "data": {
    "gender": "male",
    "birth_date": "1990-01-01",
    "height_cm": 175,
    "weight_kg": 70
  }
}
```

---

### PUT /profile

更新健康档案。

---

### GET /profile/records

获取健康记录列表。

**参数**:

- `type`: 记录类型 (blood_pressure/blood_sugar/heart_rate/weight)
- `start_date`: 开始日期
- `end_date`: 结束日期
- `limit`: 数量限制

**响应**:

```json
{
  "code": 200,
  "data": {
    "records": [
      {
        "id": "rec_xxx",
        "type": "blood_pressure",
        "value": "120/80",
        "recorded_at": "2026-02-04T10:00:00Z",
        "notes": "早晨测量"
      }
    ],
    "total": 10
  }
}
```

---

### POST /profile/records

添加健康记录。

**请求**:

```json
{
  "type": "blood_pressure",
  "value": "120/80",
  "recorded_at": "2026-02-04T10:00:00Z",
  "notes": "早晨测量"
}
```

---

### DELETE /profile/records/{record_id}

删除健康记录。

---

## 3. 医院推荐 API

### GET /hospital/search

搜索医院。

**参数**:

- `q`: 关键词
- `city`: 城市
- `level`: 等级 (三甲/三乙/二甲)
- `limit`: 数量

---

### GET /hospital/recommend

基于症状推荐医院。

**参数**:

- `department`: 推荐科室
- `lat`: 纬度
- `lng`: 经度
- `radius`: 半径 (km)

**响应**:

```json
{
  "code": 200,
  "data": {
    "hospitals": [
      {
        "id": "hosp_xxx",
        "name": "北京协和医院",
        "level": "三甲",
        "address": "北京市东城区...",
        "phone": "010-xxxx",
        "distance_km": 2.5,
        "departments": ["内科", "神经内科"]
      }
    ]
  }
}
```

---

### GET /hospital/{hospital_id}

获取医院详情。

---

## 4. 提醒服务 API

### GET /reminders

获取提醒列表。

**响应**:

```json
{
  "code": 200,
  "data": {
    "reminders": [
      {
        "id": "rem_xxx",
        "type": "medication",
        "title": "服用降压药",
        "time": "08:00",
        "repeat": "daily",
        "enabled": true
      }
    ]
  }
}
```

---

### POST /reminders

创建提醒。

**请求**:

```json
{
  "type": "medication",
  "title": "服用降压药",
  "time": "08:00",
  "repeat": "daily",
  "notes": "饭后服用"
}
```

---

### PUT /reminders/{reminder_id}

更新提醒。

---

### DELETE /reminders/{reminder_id}

删除提醒。

---

## 5. 认证说明

需要认证的接口在请求头中添加:

```
Authorization: Bearer <access_token>
```

未认证访问返回:

```json
{
  "code": 401,
  "message": "未提供认证信息"
}
```

Token 过期返回:

```json
{
  "code": 401,
  "message": "Token 无效或已过期"
}
```
