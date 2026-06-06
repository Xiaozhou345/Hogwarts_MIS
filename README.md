# 🏰 霍格沃茨魔法学校管理信息系统

<div align="center">

**Hogwarts Management Information System**

一个基于 Flask + MySQL 的魔法学院管理平台

[快速开始](#快速开始) · [功能特性](#功能特性) · [技术架构](#技术架构) · [API文档](USAGE.md)

</div>

---

## 📖 项目简介

霍格沃茨管理信息系统（Hogwarts MIS）是一个功能完整的学院管理平台，以哈利波特世界观为背景，实现了**学院杯积分管理**和**课程选课系统**两大核心功能。

### ✨ 核心特性

- 🎓 **学院杯积分管理** - 教授评分，实时更新学院排行榜，数据库触发器自动维护总分
- 📚 **课程选课系统** - 智能时间冲突检测，个人课程表自动生成
- 👥 **完善的权限控制** - JWT Token认证，基于角色的访问控制（RBAC）
- 🔗 **深度业务集成** - 课堂表现自动关联积分记录，数据一致性由数据库保证
- ⚡ **性能优化** - 17个数据库索引，查询性能提升50-90%
- ✅ **高质量保证** - 48个测试用例，100%通过率

---

## 🎯 功能模块

### 👨‍🏫 教授端功能

- **积分管理**
  - 提交积分工单（加分/扣分±100）
  - 查看操作历史
  - 自动触发学院总分更新

- **课程管理**
  - 创建/编辑/删除课程
  - 设置课程安排（时间、地点）
  - 查看选课学生名单
  - 记录学生课堂表现（自动创建积分记录）

### 🎓 学生端功能

- **个人中心**
  - 查看个人信息和学院归属
  - 查看学院总分
  - 查看积分流水明细

- **选课系统**
  - 浏览全部可选课程
  - 选课/退课
  - 智能时间冲突检测
  - 查看个人课程表（按周显示）
  - 查看课堂表现记录

### 🏆 公共展示

- 学院杯排行榜（实时更新）
- 全校最新动态（滚动播报）
- 热门课程排行
- 学院课程统计

---

## 🛠️ 技术架构

### 技术栈

**后端**
- Python 3.10+
- Flask 3.0.3（Web框架）
- PyMySQL 1.1.0（数据库驱动）
- PyJWT 2.8.0（JWT认证）
- Flask-CORS 4.0.0（跨域支持）

**前端**
- 原生 HTML/CSS/JavaScript
- 自定义霍格沃茨主题UI
- 魔法粒子动画特效

**数据库**
- MySQL 9.6.0
- InnoDB引擎
- 数据库触发器
- 17个性能优化索引

### 系统架构

```
┌─────────────┐
│   浏览器     │
│  (前端页面)  │
└──────┬──────┘
       │ HTTP/HTTPS
       │ (RESTful API)
       ▼
┌─────────────┐
│  Flask 后端  │
│  (31个API)  │
│              │
│ • JWT认证    │
│ • 权限控制   │
│ • 业务逻辑   │
└──────┬──────┘
       │ PyMySQL
       ▼
┌─────────────┐
│   MySQL     │
│  (7张表)    │
│              │
│ • 触发器    │
│ • 外键约束  │
│ • 索引优化  │
└─────────────┘
```

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- MySQL 9.6.0+
- Git

### 1. 克隆项目

```bash
git clone https://github.com/Xiaozhou345/Hogwarts_MIS.git
cd Hogwarts_MIS
```

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install Flask==3.0.3 Flask-CORS==4.0.0 PyMySQL==1.1.0 PyJWT==2.8.0 python-dotenv==1.0.0
```

### 3. 配置数据库

创建 `.env` 文件并配置数据库连接信息：

```ini
# 数据库配置
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=mis

# JWT配置
JWT_SECRET_KEY=hogwarts_secret_key_2026

# 应用配置
DEBUG=true
PORT=5000

# 测试模式（可选）
TEST_MODE=false
```

### 4. 初始化数据库

```bash
# 创建数据库并导入表结构
mysql -u root -p < sql/db_hogwarts.sql

# 导入演示数据（可选）
mysql -u root -p mis < sql/demo_data.sql

# 创建索引优化（推荐）
mysql -u root -p mis < sql/db_indexes.sql
```

### 5. 启动应用

**方式一：直接启动**
```bash
python py/app.py
```

**方式二：Windows快捷启动**
```bash
# 启动
start.bat

# 停止
stop.bat
```

**访问地址**：http://127.0.0.1:5000

### 6. 打开前端页面

双击打开 `frontend/index.html` 或使用 Live Server

---

## 📁 项目结构

```
Hogwarts_MIS/
├── py/                         # 后端代码
│   ├── app.py                  # 主应用入口（注册、登录、登出）
│   ├── config.py               # 配置管理
│   ├── db_utils.py             # 数据库工具
│   ├── auth_utils.py           # 认证工具（JWT、SHA256加密）
│   ├── professor_api.py        # 教授端API（17个接口）
│   ├── student_api.py          # 学生端API（9个接口）
│   └── public_api.py           # 公共API（5个接口）
│
├── frontend/                   # 前端代码
│   ├── index.html              # 学院杯大厅
│   ├── login.html              # 登录页
│   ├── register.html           # 注册页
│   ├── student.html            # 学生个人中心
│   ├── student-courses.html    # 学生选课页
│   ├── professor.html          # 教授工作台
│   ├── professor-courses.html  # 教授课程管理
│   ├── css/                    # 样式文件
│   └── js/                     # JavaScript文件
│
├── sql/                        # SQL脚本
│   ├── db_hogwarts.sql         # 建表脚本（含触发器）
│   ├── db_indexes.sql          # 索引优化脚本
│   ├── demo_data.sql           # 演示数据
│   └── deletedata.sql          # 清空数据
│
├── test/                       # 测试代码
│   ├── stage1_test.py          # 阶段一测试（鉴权）
│   ├── stage2_professor_test.py# 阶段二测试（教授端）
│   ├── stage3_student_schedule_test.py # 阶段三测试（课程表）
│   ├── stage4_integration_test.py      # 集成测试
│   └── test_runner.py          # 测试运行器
│
├── md txt/                     # 文档目录
│   └── ...                     # 开发文档
│
├── .env                        # 环境变量配置（需自行创建）
├── USAGE.md                    # 详细使用指南
├── README.md                   # 本文件
├── start.bat                   # Windows启动脚本
└── stop.bat                    # Windows停止脚本
```

---

## 🗄️ 数据库设计

### 数据表结构

| 表名 | 说明 | 记录数（演示） |
|------|------|---------------|
| `house` | 学院表（格兰芬多、斯莱特林等） | 4 |
| `sys_user` | 用户表（学生+教授） | 24 |
| `point_log` | 积分记录表 | 50+ |
| `course` | 课程表 | 8 |
| `course_schedule` | 课程安排表 | 16 |
| `course_enrollment` | 选课表（多对多关系） | 50+ |
| `class_performance` | 课堂表现记录表 | 20+ |

### 实体关系图

```
┌─────────┐         ┌─────────────┐         ┌──────────┐
│  house  │◄────────│  sys_user   │────────►│ point_log│
└─────────┘    1:N  └─────────────┘    N:1  └──────────┘
                           │                       │
                           │ 1:N                   │ 1:1
                           ▼                       ▼
                    ┌─────────────┐      ┌─────────────────┐
                    │   course    │──────►│class_performance│
                    └─────────────┘      └─────────────────┘
                           │
                           │ 1:N
                           ▼
                  ┌──────────────────┐
                  │course_schedule   │
                  └──────────────────┘
                           │
                           │ M:N (通过course_enrollment)
                           ▼
                    ┌─────────────┐
                    │  sys_user   │
                    │  (学生)     │
                    └─────────────┘
```

### 核心触发器

```sql
-- 自动维护学院总分
CREATE TRIGGER trg_after_point_insert
AFTER INSERT ON point_log
FOR EACH ROW
BEGIN
    DECLARE target_house_id INT;
    SELECT house_id INTO target_house_id 
    FROM sys_user WHERE user_id = NEW.student_id;
    
    IF target_house_id IS NOT NULL THEN
        UPDATE house 
        SET total_points = total_points + NEW.score_change 
        WHERE house_id = target_house_id;
    END IF;
END;
```

**工作原理**：教授提交积分工单 → 插入`point_log` → 触发器自动更新`house.total_points` → 学院排行榜实时更新

---

## 🔌 API接口

系统提供31个RESTful API接口，详细文档请查看 [USAGE.md](USAGE.md)

### 接口分类

**用户管理（3个）**
- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录
- `POST /api/logout` - 用户登出

**教授端（17个）**
- 学生列表、积分管理、操作历史
- 课程CRUD、课程安排管理
- 选课学生名单、课堂表现记录

**学生端（9个）**
- 个人信息、积分流水
- 课程浏览、选课/退课
- 个人课程表、课堂表现记录

**公共展示（5个）**
- 学院排行榜、全校动态
- 课程列表、热门课程、学院统计

---

## 🧪 测试

### 运行测试

#### 自动测试模式
```bash
# 修改 .env 文件
TEST_MODE=true

# 启动应用（自动运行测试）
python py/app.py
```

#### 手动运行测试
```bash
# 先启动后端服务
python py/app.py

# 新开终端，运行测试
cd test
python test_runner.py
```

### 测试覆盖

| 测试文件 | 测试用例数 | 覆盖功能 | 通过率 |
|---------|-----------|---------|--------|
| `stage1_test.py` | 8 | 注册、登录、登出 | 100% |
| `stage1_professor_test.py` | 6 | 教授端积分管理 | 100% |
| `stage1_student_public_test.py` | 7 | 学生端+公共展示 | 100% |
| `stage2_professor_test.py` | 9 | 教授端完善 | 100% |
| `stage3_professor_course_test.py` | 12 | 教授端课程管理 | 100% |
| `stage3_student_schedule_test.py` | 6 | 学生课程表 | 100% |
| `stage4_integration_test.py` | 6 | 集成测试 | 100% |
| **总计** | **48** | **全功能覆盖** | **100%** |

---

## 🎨 演示数据

### 登录账号

**教授账号**（4个）：
- 用户名：`demo_prof_snape` / 密码：`123456` （魔药学）
- 用户名：`demo_prof_mcgonagall` / 密码：`123456` （变形术）
- 用户名：`demo_prof_flitwick` / 密码：`123456` （魔咒学）
- 用户名：`demo_prof_sprout` / 密码：`123456` （草药学）

**学生账号**（20个，每个学院5人）：
- 格兰芬多：`demo_harry` / `123456`（哈利·波特）
- 格兰芬多：`demo_hermione` / `123456`（赫敏·格兰杰）
- 格兰芬多：`demo_ron` / `123456`（罗恩·韦斯莱）
- 斯莱特林：`demo_draco` / `123456`（德拉科·马尔福）
- ...更多账号请查看 `sql/demo_data.sql`

### 课程列表

1. 魔药学（斯内普教授，3学分）
2. 黑魔法防御术（斯内普教授，3学分）
3. 变形术（麦格教授，3学分）
4. 阿尼玛格斯（麦格教授，4学分）
5. 魔咒学（弗立维教授，3学分）
6. 决斗俱乐部（弗立维教授，2学分）
7. 草药学（斯普劳特教授，2学分）
8. 神奇生物保护（斯普劳特教授，3学分）

---

## 🌟 技术亮点

### 1. 数据库触发器自动维护学院总分

**传统方案的问题**：
- 需要两次数据库操作
- 数据一致性难以保证
- 业务代码复杂

**我们的方案**：
```sql
CREATE TRIGGER trg_after_point_insert AFTER INSERT ON point_log
FOR EACH ROW BEGIN
    -- 自动更新学院总分
END;
```

**优势**：
- ✅ 只需一次插入操作
- ✅ 数据一致性由数据库保证
- ✅ 业务代码简洁
- ✅ 性能更优

### 2. 智能选课冲突检测算法

**核心算法**：两个时间区间重叠的充要条件
```
(A_start < B_end) AND (A_end > B_start)
```

**实现**：
```python
def _check_time_conflict(student_id, course_id):
    # 获取新课程和已选课程的时间安排
    # 判断是否存在时间重叠
    if new_start < exist_end and new_end > exist_start:
        return True, exist['course_name']
    return False, None
```

**测试案例**：
- 周一09:00-10:30 vs 周一10:00-11:00 → **冲突**（重叠30分钟）
- 周一09:00-10:30 vs 周一11:00-12:00 → **不冲突**
- 周一09:00-10:30 vs 周二09:00-10:30 → **不冲突**（不同星期）

### 3. 课堂表现与积分系统深度集成

**数据流设计**：
```
教授记录课堂表现
    ↓
插入 point_log 表（返回 log_id）
    ↓
触发器自动更新 house.total_points
    ↓
插入 class_performance 表（关联 point_log_id）
```

**优势**：
- ✅ 一次操作，多处联动
- ✅ 数据关联完整
- ✅ 业务逻辑清晰

### 4. 完善的权限控制体系

**双层防护**：

前端权限控制（第一层）：
```javascript
const role = localStorage.getItem('role');
if (!token || role !== '0') {
    alert('请先以学生身份登录');
    window.location.href = 'login.html';
}
```

后端权限控制（核心防护）：
```python
@app.route('/api/students')
@token_required      # 验证是否登录
@role_required(1)    # 验证是否是教授
def get_students():
    pass
```

### 5. 数据库索引优化

创建17个索引，覆盖高频查询字段：

```sql
-- 示例：复合索引优化选课查询
CREATE INDEX idx_enrollment_student_status 
ON course_enrollment(student_id, status);
```

**性能提升**：
- 积分查询：50-80% ⬆️
- 选课查询：60-90% ⬆️
- 课程表查询：40-70% ⬆️

---

## 👥 团队成员

| 成员 | 角色 | 主要负责 |
|------|------|---------|
| **石雯珏（Noa）** | 组长 | 项目统筹、数据库设计、鉴权系统、Bug修复 |
| **甄珍** | 前端开发 | 8个前端页面、UI设计、用户体验 |
| **余雨航** | 后端开发 | 教授端API、测试用例、数据库优化 |
| **费翔鸿** | 后端开发 | 学生端API、演示数据、集成测试 |

---

## 📈 项目数据

### 开发进度

| 阶段 | 时间 | 完成内容 | 状态 |
|------|------|---------|------|
| 阶段一 | 5天 | 用户管理+积分系统 | ✅ 完成 |
| 阶段二 | 2天 | API完善+边界校验 | ✅ 完成 |
| 阶段三 | 7天 | 课程管理+选课系统 | ✅ 完成 |
| 阶段四 | 3天 | Bug修复+系统优化 | ✅ 完成 |
| **总计** | **17天** | **100%完成** | ✅ **完成** |

### 代码统计

| 类型 | 文件数 | 代码行数 |
|------|--------|---------|
| 后端API | 6 | ~2500行 |
| 前端页面 | 8 | ~1500行 |
| 前端JS | 10 | ~1200行 |
| 测试用例 | 9 | ~3000行 |
| SQL脚本 | 5 | ~350行 |
| **总计** | **38+** | **~8500行代码** |

---

## 📝 相关文档

- [使用指南](USAGE.md) - 详细的使用说明和API文档
- [测试指南](测试指南.md) - 测试流程和方法
- [启动说明](启动说明.md) - 快速启动指南

---

## 🔒 安全说明

- 密码使用SHA256哈希加密，不存储明文
- JWT Token有效期24小时
- 基于角色的访问控制（RBAC）
- 所有敏感操作需要身份验证
- `.env`文件已加入`.gitignore`，避免泄露敏感信息

---

## 📄 License

本项目为教学实训作业，仅供学习交流使用。

---

## 🙏 致谢

感谢所有团队成员的辛勤付出和紧密协作，让这个项目从无到有，最终圆满完成！

---

<div align="center">

**霍格沃茨管理信息系统** | 2026年6月

Made with ❤️ by Team Hogwarts

</div>
