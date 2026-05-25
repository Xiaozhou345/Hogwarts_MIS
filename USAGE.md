# 霍格沃茨 MIS 系统 - 使用说明

## 项目概述
霍格沃茨管理信息系统（MIS）是一个基于 B/S 架构的学院杯积分管理系统。
- **后端**: Python Flask + MySQL
- **架构**: RESTful API
- **认证**: JWT Token

## 项目结构
```
Hogwarts_MIS/
├── py/                      # Python 代码目录
│   ├── app.py              # 主应用入口
│   ├── config.py           # 配置文件
│   ├── db_utils.py         # 数据库工具
│   └── auth_utils.py       # 认证工具（JWT、密码加密）
├── test/                    # 测试代码目录
│   ├── __init__.py
│   └── stage1_test.py      # 第一阶段测试
├── sql/                     # SQL 脚本
│   └── db_hogwarts.sql     # 数据库建表脚本
├── md txt/                  # 文档目录
│   ├── Hogwarts_MIS_API_Doc.md  # API 文档
│   └── requirements.txt    # Python 依赖
├── .env                     # 环境变量配置
└── README.md               # 项目说明
```

## 快速开始

### 1. 安装依赖
```bash
pip3 install -r "md txt/requirements.txt"
```

### 2. 配置环境变量
编辑 `.env` 文件，配置数据库连接信息：
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=mis

JWT_SECRET_KEY=hogwarts_secret_key_2026

DEBUG=true
PORT=5000

# 测试模式开关 (true/false)
TEST_MODE=false
```

### 3. 初始化数据库
```bash
mysql -u root -p < sql/db_hogwarts.sql
```

### 4. 运行应用

#### 正常模式（启动服务器）
```bash
python py/app.py
```
服务器将运行在 http://127.0.0.1:5000

#### 测试模式（自动运行测试）
```bash
TEST_MODE=true python py/app.py
```
或者修改 `.env` 文件中的 `TEST_MODE=true`

## 测试开关说明

项目内置了测试开关系统，通过环境变量 `TEST_MODE` 控制：

- **TEST_MODE=false**（默认）：正常运行模式，启动 Flask 服务器
- **TEST_MODE=true**：测试模式，自动启动服务器并运行测试套件

### 测试模式特点
1. 自动启动 Flask 服务器（后台线程）
2. 等待 2 秒确保服务器就绪
3. 运行完整的测试套件
4. 显示详细的测试结果和通过率

## 已实现的 API 接口（第一阶段）

### 1. 测试数据库连接
- **路径**: `GET /api/test_db`
- **说明**: 测试数据库连接是否正常

### 2. 用户注册
- **路径**: `POST /api/register`
- **参数**:
  ```json
  {
    "username": "Harry",
    "password": "password123",
    "role": 0,
    "house_id": 1
  }
  ```
- **说明**: 
  - role: 0=学生, 1=教授
  - house_id: 1=格兰芬多, 2=斯莱特林, 3=拉文克劳, 4=赫奇帕奇
  - 教授注册时 house_id 传 null
  - 密码使用 SHA256 哈希加密
  - 自动校验用户名唯一性

### 3. 用户登录
- **路径**: `POST /api/login`
- **参数**:
  ```json
  {
    "username": "Harry",
    "password": "password123"
  }
  ```
- **返回**:
  ```json
  {
    "code": 200,
    "msg": "登录成功",
    "data": {
      "token": "jwt_token_string",
      "role": 0,
      "user_id": 1
    }
  }
  ```

### 4. 用户登出
- **路径**: `POST /api/logout`
- **请求头**: `Authorization: Bearer <token>`
- **说明**: 清理登录状态

## 认证机制

### JWT Token
- 使用 JWT 进行用户认证
- Token 有效期：24 小时
- Token 包含信息：user_id, role, exp

### 使用方式
在请求头中添加：
```
Authorization: Bearer <your_token>
```

### 装饰器
- `@token_required`: 验证用户是否登录
- `@role_required(role)`: 验证用户角色权限

## 数据库设计

### 表结构
1. **house** - 学院表
   - house_id: 学院ID
   - house_name: 学院名称
   - founder: 创始人
   - total_points: 学院总分（由触发器自动维护）

2. **sys_user** - 用户表
   - user_id: 用户ID
   - username: 用户名（唯一）
   - password_hash: 密码哈希
   - role: 角色（0=学生, 1=教授）
   - house_id: 所属学院（教授为空）

3. **point_log** - 积分记录表
   - log_id: 记录ID
   - student_id: 学生ID
   - professor_id: 教授ID
   - score_change: 分数变动
   - reason: 原因
   - create_time: 创建时间

### 触发器
- **trg_after_point_insert**: 当插入积分记录时，自动更新对应学院的总分

## 第一阶段验收标准

✅ 所有测试通过（8/8）：
1. ✅ 数据库连接测试
2. ✅ 学生注册功能
3. ✅ 教授注册功能
4. ✅ 重复用户名检测
5. ✅ 学生登录功能
6. ✅ 教授登录功能
7. ✅ 错误密码检测
8. ✅ 登出功能

## 下一步开发（第二阶段）

根据任务书，第二阶段需要实现：
1. 教授端业务写入（积分工单）
2. 学生端基础展示
3. 相关 API 接口开发

## 常见问题

### Q: 如何切换测试模式？
A: 修改 `.env` 文件中的 `TEST_MODE=true` 或在命令行中设置环境变量

### Q: 如何添加新的测试？
A: 在 `test/` 目录下创建新的测试文件，参考 `stage1_test.py` 的格式

### Q: 密码加密方式是什么？
A: 使用 SHA256 哈希算法，在 `auth_utils.py` 中实现

### Q: Token 过期了怎么办？
A: 重新调用 `/api/login` 接口获取新的 Token

## 开发团队
- **组长（后端核心与鉴权）**: Noa / 石雯珏
- **前端开发**: 甄珍
- **后端业务（写入）**: 余雨航
- **后端业务（读取）**: 费翔鸿

## 技术栈
- Python 3.10+
- Flask 3.0.3
- PyMySQL 1.1.0
- PyJWT 2.8.0
- MySQL 9.6.0
- Flask-CORS 4.0.0
