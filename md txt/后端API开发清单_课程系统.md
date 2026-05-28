# 霍格沃茨 MIS - 课程系统后端API开发清单

**更新时间**: 2026-05-28  
**状态**: 前端已完成，等待后端实现

---

## 📋 概述

前端开发（甄珍）已经完成了所有课程系统的页面和API调用封装。现在需要后端团队实现对应的API接口。

**前端新增文件**:
- ✅ `frontend/professor-courses.html` - 教授课程管理页面
- ✅ `frontend/student-courses.html` - 学生选课页面
- ✅ `frontend/js/professor-courses.js` - 教授端逻辑（364行）
- ✅ `frontend/js/student-courses.js` - 学生端逻辑（373行）
- ✅ `frontend/js/api.js` - API封装（新增20个课程相关函数）
- ✅ `frontend/css/hogwarts.css` - 课程系统样式（+328行）

---

## 🎯 需要实现的API接口（共20个）

### 一、教授端API（8个接口）- 负责人：余雨航

**文件**: `py/professor_api.py`

#### 1. 课程管理（4个接口）

##### 1.1 创建课程
```python
POST /api/professor/course
@token_required
@role_required(1)

请求体:
{
  "course_name": "魔药学",
  "credits": 3,
  "description": "学习各种魔药的配制方法"
}

返回:
{
  "code": 200,
  "msg": "课程创建成功",
  "data": {
    "course_id": 1,
    "course_name": "魔药学",
    "professor_id": 2,
    "credits": 3,
    "description": "学习各种魔药的配制方法"
  }
}
```

##### 1.2 获取教授的课程列表
```python
GET /api/professor/courses
@token_required
@role_required(1)

返回:
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "course_id": 1,
      "course_name": "魔药学",
      "credits": 3,
      "description": "...",
      "student_count": 25  // 选课人数
    }
  ]
}
```

##### 1.3 更新课程信息
```python
PUT /api/professor/course/<course_id>
@token_required
@role_required(1)

请求体:
{
  "course_name": "高级魔药学",
  "credits": 4,
  "description": "更新后的描述"
}

返回:
{
  "code": 200,
  "msg": "课程更新成功",
  "data": {...}
}

注意: 需要验证该课程是否属于当前教授
```

##### 1.4 删除课程
```python
DELETE /api/professor/course/<course_id>
@token_required
@role_required(1)

返回:
{
  "code": 200,
  "msg": "课程删除成功"
}

注意: 
- 需要验证该课程是否属于当前教授
- 删除课程时需要级联删除相关数据（课程安排、选课记录等）
```

---

#### 2. 课程安排管理（3个接口）

##### 2.1 添加课程安排
```python
POST /api/professor/course/<course_id>/schedule
@token_required
@role_required(1)

请求体:
{
  "weekday": 1,           // 1-7 (周一到周日)
  "start_time": "09:00",
  "end_time": "10:30",
  "classroom": "地下教室"
}

返回:
{
  "code": 200,
  "msg": "课程安排添加成功",
  "data": {
    "schedule_id": 1,
    "course_id": 1,
    "weekday": 1,
    "start_time": "09:00:00",
    "end_time": "10:30:00",
    "classroom": "地下教室"
  }
}
```

##### 2.2 获取课程安排
```python
GET /api/professor/course/<course_id>/schedule
@token_required
@role_required(1)

返回:
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "schedule_id": 1,
      "weekday": 1,
      "start_time": "09:00:00",
      "end_time": "10:30:00",
      "classroom": "地下教室"
    }
  ]
}
```

##### 2.3 删除课程安排
```python
DELETE /api/professor/schedule/<schedule_id>
@token_required
@role_required(1)

返回:
{
  "code": 200,
  "msg": "课程安排删除成功"
}
```

---

#### 3. 选课学生管理（1个接口）

##### 3.1 查看选课学生名单
```python
GET /api/professor/course/<course_id>/students
@token_required
@role_required(1)

返回:
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "enrollment_id": 1,
      "student_id": 5,
      "student_name": "Harry Potter",
      "house_name": "Gryffindor",
      "enroll_time": "2026-05-28T10:00:00",
      "status": 1  // 1=在读, 2=已完成, 3=已退课
    }
  ]
}
```

---

#### 4. 课堂表现记录（2个接口）

##### 4.1 记录课堂表现（核心功能）
```python
POST /api/professor/class-performance
@token_required
@role_required(1)

请求体:
{
  "student_id": 5,
  "course_id": 1,
  "performance_type": 1,  // 1=回答问题, 2=课堂作业, 3=小组合作
  "score": 10,
  "reason": "魔药学课堂回答正确"
}

返回:
{
  "code": 200,
  "msg": "课堂表现记录成功",
  "data": {
    "performance_id": 1,
    "point_log_id": 123  // 关联的积分记录ID
  }
}

实现要点:
1. 先插入 point_log 表（创建积分记录）
2. 获取 point_log_id
3. 插入 class_performance 表（关联 point_log_id）
4. 触发器会自动更新学院总分

示例代码:
# 1. 插入积分记录
point_sql = """
    INSERT INTO point_log (student_id, professor_id, score_change, reason)
    VALUES (%s, %s, %s, %s)
"""
point_log_id = execute_query(point_sql, 
    (student_id, professor_id, score, reason),
    return_lastrowid=True
)

# 2. 插入课堂表现记录
perf_sql = """
    INSERT INTO class_performance 
    (student_id, course_id, professor_id, performance_type, score, point_log_id)
    VALUES (%s, %s, %s, %s, %s, %s)
"""
execute_query(perf_sql, 
    (student_id, course_id, professor_id, performance_type, score, point_log_id)
)
```

##### 4.2 查看课程的课堂表现记录
```python
GET /api/professor/course/<course_id>/performances
@token_required
@role_required(1)

返回:
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "performance_id": 1,
      "student_name": "Harry Potter",
      "performance_type": 1,
      "score": 10,
      "reason": "魔药学课堂回答正确",
      "create_time": "2026-05-28T14:30:00"
    }
  ]
}
```

---

### 二、学生端API（7个接口）- 负责人：费翔鸿

**文件**: `py/student_api.py`

#### 1. 课程浏览（2个接口）

##### 1.1 获取所有可选课程
```python
GET /api/student/courses/available
@token_required
@role_required(0)

返回:
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "course_id": 1,
      "course_name": "魔药学",
      "professor_name": "Snape",
      "credits": 3,
      "description": "...",
      "student_count": 25,  // 已选人数
      "is_enrolled": false  // 当前学生是否已选
    }
  ]
}

实现要点:
- 查询所有课程
- 联查教授姓名
- 统计每门课的选课人数
- 标记当前学生是否已选该课程
```

##### 1.2 获取课程详情
```python
GET /api/student/course/<course_id>
@token_required
@role_required(0)

返回:
{
  "code": 200,
  "msg": "success",
  "data": {
    "course_id": 1,
    "course_name": "魔药学",
    "professor_name": "Snape",
    "credits": 3,
    "description": "...",
    "student_count": 25,
    "schedules": [  // 课程安排
      {
        "weekday": 1,
        "start_time": "09:00:00",
        "end_time": "10:30:00",
        "classroom": "地下教室"
      }
    ]
  }
}
```

---

#### 2. 选课管理（3个接口）

##### 2.1 选课
```python
POST /api/student/enroll
@token_required
@role_required(0)

请求体:
{
  "course_id": 1
}

返回:
{
  "code": 200,
  "msg": "选课成功",
  "data": {
    "enrollment_id": 1,
    "course_name": "魔药学"
  }
}

校验要点:
1. 检查是否已选该课程
2. 检查课程时间是否与已选课程冲突

时间冲突检测SQL:
SELECT COUNT(*) as conflict_count
FROM course_enrollment ce1
JOIN course_schedule cs1 ON ce1.course_id = cs1.course_id
JOIN course_schedule cs2 ON cs2.course_id = %s
WHERE ce1.student_id = %s 
  AND ce1.status = 1
  AND cs1.weekday = cs2.weekday
  AND (
      (cs1.start_time <= cs2.start_time AND cs1.end_time > cs2.start_time)
      OR
      (cs1.start_time < cs2.end_time AND cs1.end_time >= cs2.end_time)
  )
```

##### 2.2 退课
```python
DELETE /api/student/enroll/<enrollment_id>
@token_required
@role_required(0)

返回:
{
  "code": 200,
  "msg": "退课成功"
}

注意: 需要验证该选课记录是否属于当前学生
```

##### 2.3 查看我的选课列表
```python
GET /api/student/my-courses
@token_required
@role_required(0)

返回:
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "enrollment_id": 1,
      "course_id": 1,
      "course_name": "魔药学",
      "professor_name": "Snape",
      "credits": 3,
      "enroll_time": "2026-05-28T10:00:00",
      "status": 1
    }
  ]
}
```

---

#### 3. 课程表查询（1个接口）

##### 3.1 获取个人课程表（核心功能）
```python
GET /api/student/schedule
@token_required
@role_required(0)

返回:
{
  "code": 200,
  "msg": "success",
  "data": {
    "Monday": [
      {
        "course_name": "魔药学",
        "professor_name": "Snape",
        "start_time": "09:00:00",
        "end_time": "10:30:00",
        "classroom": "地下教室",
        "course_id": 1
      }
    ],
    "Tuesday": [],
    "Wednesday": [...],
    "Thursday": [],
    "Friday": [],
    "Saturday": [],
    "Sunday": []
  }
}

实现要点:
1. 查询学生的所有选课
2. 联查课程安排
3. 按星期分组
4. 按时间排序

示例SQL:
SELECT 
    c.course_id,
    c.course_name,
    cs.weekday,
    cs.start_time,
    cs.end_time,
    cs.classroom,
    p.username AS professor_name
FROM course_enrollment ce
JOIN course c ON ce.course_id = c.course_id
JOIN course_schedule cs ON c.course_id = cs.course_id
JOIN sys_user p ON c.professor_id = p.user_id
WHERE ce.student_id = %s AND ce.status = 1
ORDER BY cs.weekday, cs.start_time

然后在Python中按weekday分组
```

---

#### 4. 课堂表现查询（1个接口）

##### 4.1 查看我的课堂表现记录
```python
GET /api/student/my-performances
@token_required
@role_required(0)

返回:
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "performance_id": 1,
      "course_name": "魔药学",
      "professor_name": "Snape",
      "performance_type": 1,
      "score": 10,
      "reason": "魔药学课堂回答正确",
      "create_time": "2026-05-28T14:30:00"
    }
  ]
}
```

---

### 三、公共API（3个接口）- 负责人：费翔鸿

**文件**: `py/public_api.py`

#### 3.1 获取所有课程（无需登录）
```python
GET /api/public/courses

返回:
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "course_id": 1,
      "course_name": "魔药学",
      "professor_name": "Snape",
      "credits": 3,
      "student_count": 25
    }
  ]
}
```

#### 3.2 热门课程排行（按选课人数）
```python
GET /api/public/courses/popular

返回:
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "course_id": 1,
      "course_name": "魔药学",
      "professor_name": "Snape",
      "student_count": 30
    }
  ]
}

实现: ORDER BY student_count DESC LIMIT 10
```

#### 3.3 学院课程统计
```python
GET /api/public/courses/house-stats

返回:
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "house_name": "Gryffindor",
      "course_name": "魔药学",
      "avg_score": 85.5,
      "student_count": 15
    }
  ]
}

实现要点:
- 统计各学院在各门课程的平均课堂表现分数
- 需要联查多个表
```

---

## 🔧 数据库工具函数扩展

在 `py/db_utils.py` 中可能需要添加：

```python
def execute_query(sql, params=None, fetch_one=False, fetch_all=False, return_lastrowid=False):
    """
    新增 return_lastrowid 参数
    用于插入数据后返回自增ID
    """
    # ... 现有代码 ...
    
    if return_lastrowid:
        return cursor.lastrowid
```

---

## ✅ 开发检查清单

### 教授端（余雨航）
- [ ] POST /api/professor/course - 创建课程
- [ ] GET /api/professor/courses - 获取课程列表
- [ ] PUT /api/professor/course/<id> - 更新课程
- [ ] DELETE /api/professor/course/<id> - 删除课程
- [ ] POST /api/professor/course/<id>/schedule - 添加课程安排
- [ ] GET /api/professor/course/<id>/schedule - 获取课程安排
- [ ] DELETE /api/professor/schedule/<id> - 删除课程安排
- [ ] GET /api/professor/course/<id>/students - 查看选课学生
- [ ] POST /api/professor/class-performance - 记录课堂表现（关联积分）
- [ ] GET /api/professor/course/<id>/performances - 查看课堂表现记录

### 学生端（费翔鸿）
- [ ] GET /api/student/courses/available - 浏览可选课程
- [ ] GET /api/student/course/<id> - 课程详情
- [ ] POST /api/student/enroll - 选课（含冲突检测）
- [ ] DELETE /api/student/enroll/<id> - 退课
- [ ] GET /api/student/my-courses - 我的选课列表
- [ ] GET /api/student/schedule - 个人课程表（按周显示）
- [ ] GET /api/student/my-performances - 我的课堂表现记录

### 公共接口（费翔鸿）
- [ ] GET /api/public/courses - 所有课程
- [ ] GET /api/public/courses/popular - 热门课程排行
- [ ] GET /api/public/courses/house-stats - 学院课程统计

---

## 🧪 测试要求

每个接口都需要编写测试用例，包括：
1. 正常情况测试
2. 边界情况测试
3. 权限验证测试
4. 错误处理测试

**测试文件**: `test/stage3_course_test.py`

---

## ⏰ 时间安排建议

### Day 1-2（余雨航）
- 实现教授端课程CRUD（4个接口）
- 实现课程安排管理（3个接口）

### Day 3（余雨航）
- 实现选课学生查询（1个接口）
- **核心**：实现课堂表现记录（2个接口，关联积分系统）

### Day 1-2（费翔鸿）
- 实现学生端课程浏览（2个接口）
- 实现选课/退课（3个接口，含冲突检测）

### Day 3（费翔鸿）
- **核心**：实现个人课程表查询（1个接口，复杂SQL）
- 实现课堂表现查询（1个接口）
- 实现公共统计接口（3个接口）

### Day 4-5（全员）
- 前后端联调测试
- 修复bug
- 编写测试用例

---

## 📝 注意事项

### 1. 权限控制
- 教授只能管理自己的课程
- 学生只能操作自己的选课记录
- 公共接口无需登录

### 2. 数据一致性
- 课堂表现必须同时创建积分记录
- 使用事务确保数据一致性
- 删除课程时级联删除相关数据

### 3. 边界校验
- 选课冲突检测
- 重复选课检测
- 课程归属验证

### 4. 性能优化
- 使用JOIN减少查询次数
- 避免N+1查询问题
- 在常用查询字段上建立索引

---

**文档生成时间**: 2026-05-28  
**负责人**: 石雯珏 (Noa)
