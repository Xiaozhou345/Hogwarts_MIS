# 霍格沃茨管理信息系统(MIS)-API接口文档

本选型方案基于B/S架构，后端采用Python(Flask/FastAPI)，数据库采用MySQL。本系统核心业务流程为“学院杯积分动态管理”。

## 1.全局说明
* **基础路径(BaseURL)**:`/api`
* **数据格式**:`application/json`
* **统一响应体格式**:
```json
{
"code":200,//状态码:200成功,400参数错误,401未授权,500服务器错误
"msg":"success",//提示信息
"data":null//具体业务数据
}
```

---

## 2.用户管理模块(组员2负责)

### 2.1用户注册
* **请求路径**:`POST/api/register`
* **请求参数**:
```json
{
"username":"Harry",
"password":"password123",
"role":0,//0:学生,1:教授
"house_id":1//学院ID:1格兰芬多,2斯莱特林,3拉文克劳,4赫奇帕奇(教授传null)
}
```
* **业务逻辑**:校验用户名唯一性；密码需进行哈希加密后再写入`sys_user`表。
* **返回示例**:
```json
{
"code":200,
"msg":"注册成功",
"data":null
}
```

### 2.2用户登录
* **请求路径**:`POST/api/login`
* **请求参数**:
```json
{
"username":"Noa",
"password":"password123"
}
```
* **业务逻辑**:校验用户名和密码；成功后生成鉴权凭证(Token/Session)，并返回角色。
* **返回示例**:
```json
{
"code":200,
"msg":"登录成功",
"data":{
"token":"jwt_token_string",
"role":0,
"user_id":24301132
}
}
```

### 2.3退出登录
* **请求路径**:`POST/api/logout`
* **请求参数**:无(请求头需携带Token)
* **业务逻辑**:清理服务端的登录会话状态。
* **返回示例**:
```json
{
"code":200,
"msg":"已安全退出",
"data":null
}
```

---

## 3.教授端工作台(组员3负责)

### 3.1获取学生下拉列表
* **请求路径**:`GET/api/students`
* **请求参数**:无(请求头需携带教授Token)
* **业务逻辑**:查询`sys_user`表中所有`role=0`(学生)的记录，用于工单的候选人下拉框。
* **返回示例**:
```json
{
"code":200,
"msg":"success",
"data":[
{
"user_id":24301132,
"username":"Noa",
"house_id":2
}
]
}
```

### 3.2提交积分工单(加分/扣分)
* **请求路径**:`POST/api/points`
* **请求参数**:
```json
{
"student_id":24301132,
"score_change":10,//正数为加分,负数为扣分
"reason":"魔药课完美配置福灵剂"
}
```
* **业务逻辑**:向`point_log`表插入一条变动记录。该操作会触发MySQL数据库中的`trg_after_point_insert`触发器，自动计算并更新`house`表中的各学院总分。
* **返回示例**:
```json
{
"code":200,
"msg":"积分工单提交成功",
"data":null
}
```

### 3.3获取教授操作历史
* **请求路径**:`GET/api/professor/logs`
* **请求参数**:无(请求头需携带教授Token)
* **业务逻辑**:多表联查`point_log`与`sys_user`表，获取当前登录教授名下的所有评分流水，按时间降序排列。
* **返回示例**:
```json
{
"code":200,
"msg":"success",
"data":[
{
"log_id":101,
"student_name":"Noa",
"score_change":10,
"reason":"魔药课完美配置福灵剂",
"create_time":"2026-05-20T19:46:00"
}
]
}
```

---

## 4.学生端个人中心(组员4负责)

### 4.1获取个人主页信息
* **请求路径**:`GET/api/student/info`
* **请求参数**:无(请求头需携带学生Token)
* **业务逻辑**:联查`sys_user`表与`house`表，获取当前登录学生的姓名、所属学院名称及学院总积分。
* **返回示例**:
```json
{
"code":200,
"msg":"success",
"data":{
"username":"Noa",
"house_name":"Slytherin",
"total_points":150
}
}
```

### 4.2获取个人积分通知流水
* **请求路径**:`GET/api/student/logs`
* **请求参数**:无(请求头需携带学生Token)
* **业务逻辑**:查询`point_log`中所有`student_id`等于当前登录学生的流水记录，关联教授姓名，按时间降序排列。
* **返回示例**:
```json
{
"code":200,
"msg":"success",
"data":[
{
"log_id":101,
"professor_name":"Snape",
"score_change":10,
"reason":"魔药课完美配置福灵剂",
"create_time":"2026-05-20T19:46:00"
}
]
}
```

---

## 5.学院杯大厅公共展示模块(组员4负责)

### 5.1实时沙漏排行榜
* **请求路径**:`GET/api/house/ranking`
* **请求参数**:无
* **业务逻辑**:查询`house`表的所有学院信息，按`total_points`字段从高到低排序。
* **返回示例**:
```json
{
"code":200,
"msg":"success",
"data":[
{
"house_id":2,
"house_name":"Slytherin",
"total_points":300
},
{
"house_id":1,
"house_name":"Gryffindor",
"total_points":280
},
{
"house_id":3,
"house_name":"Ravenclaw",
"total_points":240
},
{
"house_id":4,
"house_name":"Hufflepuff",
"total_points":210
}
]
}
```

### 5.2全校最新积分动态
* **请求路径**:`GET/api/public/logs`
* **请求参数**:无
* **业务逻辑**:联查`point_log`、`sys_user`(学生)、`sys_user`(教授)表，获取全校最新的10条积分变动记录，按时间降序排列。
* **返回示例**:
```json
{
"code":200,
"msg":"success",
"data":[
{
"student_name":"Noa",
"professor_name":"Snape",
"score_change":10,
"reason":"魔药课完美配置福灵剂",
"create_time":"2026-05-20T19:46:00"
}
]
}
```