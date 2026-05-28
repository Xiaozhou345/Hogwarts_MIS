# 霍格沃茨 MIS 系统 - 使用说明

## 项目概述
霍格沃茨管理信息系统（MIS）是一个基于 B/S 架构的学院杯积分管理系统。
- **后端**: Python Flask + MySQL
- **架构**: RESTful API
- **认证**: JWT Token

## 项目结构
```
Hogwarts_MIS/
├── py/                          # Python 代码目录
│   ├── app.py                   # 主应用入口（Flask 路由 + Blueprint 注册）
│   ├── config.py                # 配置文件（数据库、JWT、Debug、测试模式）
│   ├── db_utils.py              # 数据库工具（连接、execute_query 通用方法）
│   ├── auth_utils.py            # 认证工具（SHA256 密码加密、JWT 生成/验证、装饰器）
│   ├── professor_api.py         # ★ 教授端业务 API（Blueprint）
│   ├── student_api.py           # ★ 学生端业务 API（Blueprint）
│   └── public_api.py            # ★ 公共展示 API（Blueprint）
├── test/                        # 测试代码目录
│   ├── __init__.py
│   ├── test_runner.py           # ★ 测试调度器（统一入口，支持按模块选择）
│   ├── stage1_test.py           # 阶段一-鉴权测试（注册、登录、登出）[Noa]
│   ├── stage1_professor_test.py # ★ 阶段一-教授端测试（API、触发器验证）
│   ├── stage1_student_public_test.py # ★ 阶段一-学生端+公共模块测试
│   └── stage2_professor_test.py # ★ 阶段二-教授端完善测试（边界校验、分页）
├── sql/                         # SQL 脚本
│   ├── db_hogwarts.sql          # 数据库建表脚本（含触发器）
│   └── test_trigger.sql         # ★ 触发器验证 SQL 测试用例
├── md txt/                      # 文档目录
│   ├── Hogwarts_MIS_API_Doc.md  # API 接口文档（前后端契约）
│   ├── requirements.txt         # Python 依赖
│   ├── 阶段一.md                # 第一阶段任务书
│   ├── 程序说明持续更新5.26.md  # 程序更新记录
│   └── USAGE.md                 # ★ 本文件
├── .env                         # 环境变量配置
├── .env.example                 # 环境变量模板
├── .gitignore
└── README.md                    # 项目说明
```

## 快速开始

### 1. 安装依赖
```bash
pip3 install -r "md txt/requirements.txt"
```

### 2. 配置环境变量
从 `.env.example` 复制为 `.env`，编辑数据库连接信息：
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=hogwartsmis

JWT_SECRET_KEY=hogwarts_secret_key_2026

DEBUG=true
PORT=5000

# 测试模式开关 (true/false)
TEST_MODE=false

# 测试套件选择（仅在 TEST_MODE=true 时生效）
# "all" = 运行全部测试
# "auth" = 仅阶段一鉴权测试
# "professor" = 仅阶段一教授端测试
# "student" = 仅阶段一学生端+公共测试
# "professor2" = 仅阶段二教授端完善测试
# "auth,professor" = 同时运行多个套件
TEST_SUITE=all
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
将 `.env` 中 `TEST_MODE` 设为 `true`，然后：
```bash
python py/app.py
```
服务器会在后台启动，自动运行 `TEST_SUITE` 指定的测试套件。

## 测试调度器说明

项目内置了测试调度器（`test/test_runner.py`），支持按模块选择性运行测试。

### 环境变量控制

| 变量 | 值 | 说明 |
|---|---|---|
| TEST_MODE | `true` / `false` | 是否开启测试模式 |
| TEST_SUITE | `all` | 运行全部测试（默认） |
| | `auth` | 仅运行阶段一鉴权测试（注册、登录、登出） |
| | `professor` | 仅运行阶段一教授端测试（积分工单、触发器） |
| | `student` | 仅运行阶段一学生端+公共模块测试 |
| | `professor2` | 仅运行阶段二教授端完善测试（边界校验、分页） |
| | `auth,professor` | 同时运行多个测试套件 |

### 命令行手动运行
```bash
python test/test_runner.py                 # 交互式菜单选择
python test/test_runner.py --all           # 全部测试
python test/test_runner.py auth            # 仅鉴权测试
python test/test_runner.py professor       # 仅教授端测试
python test/test_runner.py student         # 仅学生端+公共测试
python test/test_runner.py professor2      # 仅阶段二教授端测试
python test/test_runner.py auth,professor  # 选中多个
```

## 已实现的 API 接口（阶段一 + 阶段二）

### 用户管理模块（组员2 Noa）

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/test_db` | GET | 测试数据库连接 |
| `/api/register` | POST | 用户注册（SHA256 密码加密 + 用户名唯一性校验） |
| `/api/login` | POST | 用户登录（返回 JWT Token + role） |
| `/api/logout` | POST | 退出登录（需 Token） |

### 教授端工作台（组员3 余雨航）— 阶段二已完善

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/students` | GET | 获取学生下拉列表（含学院名称，需教授 Token，角色校验） |
| `/api/points` | POST | 提交积分工单（加分/扣分 ±100 限制、事由 200 字限制、学院校验，触发器自动更新学院总分） |
| `/api/professor/logs` | GET | 获取教授操作历史（多表联查、时间降序、支持分页 `?page=&limit=`） |

**阶段二新增增强：**
- `GET /api/students`：联查 `house` 表返回 `house_name`，前端可直接显示学院名
- `POST /api/points`：新增分数范围校验（±100）、事由长度校验（≤200字符）、学生学院校验
- `GET /api/professor/logs`：新增分页参数 `page`/`limit`，返回 `total`/`page`/`limit` 分页信息

### 学生端个人中心（组员4 费翔鸿）

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/student/info` | GET | 获取学生个人信息（联查 house 表，返回学院信息，需学生 Token） |
| `/api/student/logs` | GET | 获取个人积分流水（支持分页 `?page=&limit=`，含教授姓名） |

### 学院杯大厅公共展示（组员4 费翔鸿）

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/house/ranking` | GET | 学院实时沙漏排行榜（按总分降序，无需登录） |
| `/api/public/logs` | GET | 全校最新积分动态（支持 `?limit=` 参数，默认10条，最大50条，无需登录） |

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
- `@role_required(1)`: 验证用户角色权限（如教授专属接口）

## 数据库设计

### 表结构
1. **house** - 学院表
   - house_id: 学院ID / house_name: 学院名称 / founder: 创始人
   - total_points: 学院总分（由触发器自动维护）

2. **sys_user** - 用户表
   - user_id: 用户ID / username: 用户名（唯一） / password_hash: 密码哈希
   - role: 角色（0=学生, 1=教授） / house_id: 所属学院（教授为空）

3. **point_log** - 积分记录表
   - log_id: 记录ID / student_id: 学生ID / professor_id: 教授ID
   - score_change: 分数变动（正数加分, 负数扣分） / reason: 原因 / create_time: 创建时间

### 触发器
- **trg_after_point_insert**: 当 `point_log` 插入新记录时，自动更新对应学院的 `total_points`

### 手动验证触发器
```bash
mysql -u root -p < sql/test_trigger.sql
```
该脚本会：查看触发器是否存在 → 记录加分前总分 → 插入积分 → 查看加分后总分 → 自动输出 `【PASS】` 或 `【FAIL】`

## 阶段一验收标准

### 鉴权测试（组员2 Noa）— 8/8 全部通过 ✅
1. ✅ 数据库连接测试
2. ✅ 学生注册功能
3. ✅ 教授注册功能
4. ✅ 重复用户名检测
5. ✅ 学生登录功能
6. ✅ 教授登录功能
7. ✅ 错误密码检测
8. ✅ 登出功能

### 教授端测试（组员3 余雨航）— 6/6 全部通过 ✅
1. ✅ 获取学生列表
2. ✅ 提交加分工单
3. ✅ 提交扣分工单
4. ✅ 触发器自动更新学院总分
5. ✅ 获取教授操作历史
6. ✅ 权限验证（学生越权访问）

### 学生端+公共测试（组员4 费翔鸿）— 7/7 全部通过 ✅
1. ✅ 获取学生个人信息
2. ✅ 获取学生积分流水
3. ✅ 学生积分流水分页
4. ✅ 学院排行榜查询
5. ✅ 全校最新积分动态
6. ✅ 积分动态限制条数
7. ✅ 权限验证（教授越权访问学生接口）

> **阶段一汇总：21/21 测试全部通过，通过率 100%**

## 阶段二验收标准（教授端完善）

### 阶段二教授端测试（组员3 余雨航）— 9/9 全部通过 ✅
1. ✅ 学生列表含学院名称
2. ✅ 正常提交积分工单（含返回数据验证）
3. ✅ 超额加分拦截（>+100 被拒绝）
4. ✅ 超额扣分拦截（>-100 被拒绝）
5. ✅ 空事由拦截
6. ✅ 超长事由拦截（>200 字符）
7. ✅ 操作历史分页功能
8. ✅ 操作历史总数与数据库一致
9. ✅ 触发器集成验证

> **阶段二教授端汇总：9/9 测试全部通过，通过率 100%**
> 
> **全量汇总：30/30 测试全部通过，通过率 100%**

## 常见问题

### Q: 如何切换测试模式？
A: 修改 `.env` 文件中的 `TEST_MODE=true` 或在命令行中设置环境变量

### Q: 如何只运行部分测试？
A: 设置 `.env` 中的 `TEST_SUITE` 变量，或直接运行 `python test/test_runner.py` 交互选择

### Q: 如何添加新的测试？
A: 在 `test/` 目录下创建新的测试文件，在 `test_runner.py` 的 `TEST_SUITES` 字典中注册

### Q: 密码加密方式是什么？
A: 使用 SHA256 哈希算法，在 `auth_utils.py` 中实现

### Q: Token 过期了怎么办？
A: 重新调用 `/api/login` 接口获取新的 Token

### Q: 终端中文乱码怎么办？
A: 在终端中执行 `chcp 65001` 切换到 UTF-8 编码，或使用 Windows Terminal

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

---

> 更新日期：2026-05-28
