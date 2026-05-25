# 霍格沃茨管理信息系统(MIS)

本项目为关系数据库管理信息系统实训作业。系统基于B/S架构，除实现基础的用户管理(注册/登录)外，重点设计并实现了核心业务流程：**学院杯积分动态管理**。

## 项目状态
✅ **第一阶段已完成** - 基础建设与鉴权系统（2026-05-25）
- 数据库连接与配置
- 用户注册/登录/登出 API
- JWT Token 认证机制
- 密码哈希加密（SHA256）
- 测试开关系统
- 完整的测试套件（通过率 100%）

## 核心技术栈
* **前端**: 待定(采用B/S架构，通过浏览器访问)
* **后端**: Python 3.10 + Flask 3.0.3
* **数据库**: MySQL 9.6.0 (采用InnoDB引擎，利用触发器与外键约束保证数据一致性)
* **认证**: JWT (PyJWT 2.8.0)
* **跨域**: Flask-CORS 4.0.0

## 团队成员与分工
本项目由4人小组共同完成：
* **组长**: 负责项目统筹、数据库底座设计、后端基础架构搭建及用户鉴权API开发。
* **组员1**: 负责全部浏览器端页面UI绘制、表单验证及前后端接口数据联调。
* **组员2**: 负责教授端工作台API(核心业务数据写入与积分工单生成)。
* **组员3**: 负责学生端及公共大厅API(多表联合聚合查询与排行榜数据读取)。

## 快速启动指南

### 1. 数据库初始化
1. 在本地环境安装MySQL
2. 使用MySQL客户端运行 `sql/db_hogwarts.sql` 文件
3. 该脚本会自动完成建库建表(`house`,`sys_user`,`point_log`)、注入基础学院数据，并创建自动化统计总分的数据库触发器(`trg_after_point_insert`)

```bash
mysql -u root -p < sql/db_hogwarts.sql
```

### 2. 后端环境配置

**步骤一: 安装依赖**
```bash
pip3 install -r "md txt/requirements.txt"
```

**步骤二: 配置环境变量**
编辑 `.env` 文件，配置你的数据库信息：
```ini
# Database Configuration
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_local_password
DB_NAME=mis

# JWT Configuration
JWT_SECRET_KEY=hogwarts_secret_key_2026

# Application Configuration
DEBUG=true
PORT=5000

# Test Mode (true/false)
TEST_MODE=false
```
*注意: `.env`文件已加入忽略名单，切勿将真实密码提交至远程仓库。*

### 3. 运行应用

**正常模式（启动服务器）**
```bash
python py/app.py
```
服务器将运行在 http://127.0.0.1:5000

**测试模式（自动运行测试）**
```bash
TEST_MODE=true python py/app.py
```
或修改 `.env` 中的 `TEST_MODE=true`

## 项目结构
```
Hogwarts_MIS/
├── py/                      # Python 代码目录
│   ├── app.py              # 主应用入口（包含注册/登录/登出API）
│   ├── config.py           # 配置管理（数据库、JWT、测试开关）
│   ├── db_utils.py         # 数据库工具函数
│   └── auth_utils.py       # 认证工具（JWT、密码加密、装饰器）
├── test/                    # 测试代码目录
│   ├── __init__.py
│   └── stage1_test.py      # 第一阶段测试套件
├── sql/                     # SQL 脚本
│   └── db_hogwarts.sql     # 数据库建表脚本
├── md txt/                  # 文档目录
│   ├── Hogwarts_MIS_API_Doc.md  # API 接口文档
│   └── requirements.txt    # Python 依赖清单
├── .env                     # 环境变量配置
├── USAGE.md                # 详细使用说明
└── README.md               # 项目说明（本文件）
```

## 测试开关系统

项目内置了智能测试开关，通过 `.env` 中的 `TEST_MODE` 控制：

- **TEST_MODE=false**（默认）: 正常运行模式，启动 Flask 服务器
- **TEST_MODE=true**: 测试模式，自动启动服务器并运行完整测试套件

测试模式会自动：
1. 启动 Flask 服务器（后台线程）
2. 运行所有测试用例
3. 显示详细的测试结果和通过率

## 已实现的功能（第一阶段）

### API 接口
✅ `GET /api/test_db` - 测试数据库连接  
✅ `POST /api/register` - 用户注册（支持学生/教授，密码哈希加密）  
✅ `POST /api/login` - 用户登录（返回 JWT Token）  
✅ `POST /api/logout` - 用户登出  

### 核心特性
- JWT Token 认证机制（24小时有效期）
- SHA256 密码哈希加密
- 用户名唯一性校验
- 角色权限控制（学生/教授）
- 完整的错误处理
- 跨域支持（CORS）

### 测试覆盖
- 数据库连接测试
- 学生注册功能
- 教授注册功能
- 重复用户名检测
- 学生登录功能
- 教授登录功能
- 错误密码检测
- 登出功能

**当前测试通过率: 100% (8/8)**

## 接口文档
本项目严格采用前后端分离开发模式。所有数据交互规范(请求路径、参数格式、JSON响应体)请参阅：
- 📘 [API 接口文档](md%20txt/Hogwarts_MIS_API_Doc.md)
- 📗 [详细使用说明](USAGE.md)

## 开发进度

### ✅ 第一阶段（已完成）- 基础建设与鉴权
- [x] 统一数据库模型
- [x] 初始化后端项目
- [x] 编写鉴权 API 接口
- [x] 创建测试开关系统
- [x] 完成测试套件

### 🔄 第二阶段（进行中）- 教授端与学生端业务
- [ ] 教授端：获取学生列表 API
- [ ] 教授端：提交积分工单 API
- [ ] 教授端：操作历史查询 API
- [ ] 学生端：个人信息查询 API
- [ ] 学生端：积分流水查询 API

### ⏳ 第三阶段（待开始）- 公共展示模块
- [ ] 学院杯排行榜 API
- [ ] 全校积分动态 API

### ⏳ 第四阶段（待开始）- 系统测试与优化
- [ ] 全局系统测试
- [ ] Bug 修复
- [ ] 性能优化
- [ ] 答辩材料准备

## 常见问题

**Q: 如何切换测试模式？**  
A: 修改 `.env` 文件中的 `TEST_MODE=true` 或在命令行设置环境变量

**Q: Token 过期了怎么办？**  
A: 重新调用 `/api/login` 接口获取新的 Token

**Q: 如何添加新的 API 接口？**  
A: 在 `py/app.py` 中添加新的路由函数，使用 `@token_required` 装饰器进行认证

**Q: 如何为新功能添加测试？**  
A: 在 `test/` 目录下创建新的测试文件，参考 `stage1_test.py` 的格式

## 技术亮点
- 🔐 完整的 JWT 认证体系
- 🧪 自动化测试系统（测试开关）
- 🏗️ 模块化代码结构
- 🔒 密码哈希加密（SHA256）
- 🎯 RESTful API 设计
- 🔄 数据库触发器自动维护学院总分
- 📝 详细的代码注释和文档

## License
本项目为教学实训作业，仅供学习交流使用。
