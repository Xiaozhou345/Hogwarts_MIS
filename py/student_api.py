# student_api.py - 学生端个人中心 + 选课/课程表/课堂表现（第三阶段）+ 时间转换器功能
from flask import Blueprint, jsonify, request
from db_utils import execute_query
from auth_utils import token_required, role_required
from datetime import time
from time_turner_utils import (
    check_student_has_time_turner,
    get_student_house_rank,
    check_time_slot_has_course,
    check_activity_already_enrolled_at_time
)

student_bp = Blueprint('student', __name__)

# ==================== 原有接口（保留） ====================

@student_bp.route('/api/student/info', methods=['GET'])
@token_required
@role_required(0)
def get_student_info():
    """学生个人信息查询"""
    try:
        user_id = request.user_id
        sql = """
            SELECT u.username, u.house_id, h.house_name, h.total_points
            FROM sys_user u
            LEFT JOIN house h ON u.house_id = h.house_id
            WHERE u.user_id = %s AND u.role = 0
        """
        student = execute_query(sql, (user_id,), fetch_one=True)
        if not student:
            return jsonify({"code": 404, "msg": "学生不存在", "data": None}), 404
        return jsonify({"code": 200, "msg": "success", "data": student})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@student_bp.route('/api/student/logs', methods=['GET'])
@token_required
@role_required(0)
def get_student_points_logs():
    """学生积分变动明细（分页）"""
    try:
        user_id = request.user_id
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        offset = (page - 1) * limit

        count_sql = "SELECT COUNT(*) as total FROM point_log WHERE student_id = %s"
        count_result = execute_query(count_sql, (user_id,), fetch_one=True)
        total = count_result['total'] if count_result else 0

        sql = """
            SELECT pl.log_id, pl.score_change, pl.reason, pl.create_time,
                   p.username AS professor_name
            FROM point_log pl
            JOIN sys_user p ON pl.professor_id = p.user_id
            WHERE pl.student_id = %s
            ORDER BY pl.create_time DESC
            LIMIT %s OFFSET %s
        """
        logs = execute_query(sql, (user_id, limit, offset), fetch_all=True)
        for log in logs:
            if hasattr(log['create_time'], 'isoformat'):
                log['create_time'] = log['create_time'].isoformat()
        return jsonify({
            "code": 200,
            "msg": "success",
            "data": {"logs": logs, "total": total, "page": page, "limit": limit}
        })
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


# ==================== 第三阶段新增：课程浏览 ====================

@student_bp.route('/api/student/courses/available', methods=['GET'])
@token_required
@role_required(0)
def get_available_courses():
    """
    获取所有可选课程（未被学生选过的课）
    支持搜索：?keyword=魔药
    """
    try:
        student_id = request.user_id
        keyword = request.args.get('keyword', '').strip()

        sql = """
            SELECT c.course_id, c.course_name, c.credits, c.description,
                   p.username AS professor_name,
                   (SELECT COUNT(*) FROM course_enrollment ce WHERE ce.course_id = c.course_id AND ce.status = 1) AS enrollment_count
            FROM course c
            JOIN sys_user p ON c.professor_id = p.user_id
            WHERE c.course_id NOT IN (
                SELECT course_id FROM course_enrollment 
                WHERE student_id = %s AND status = 1
            )
        """
        params = [student_id]
        if keyword:
            sql += " AND c.course_name LIKE %s"
            params.append(f"%{keyword}%")
        sql += " ORDER BY c.course_id"

        courses = execute_query(sql, tuple(params), fetch_all=True)
        return jsonify({"code": 200, "msg": "success", "data": courses})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@student_bp.route('/api/student/course/<int:course_id>', methods=['GET'])
@token_required
@role_required(0)
def get_course_detail(course_id):
    """课程详情（含课程安排、教授信息、选课人数）"""
    try:
        sql = """
            SELECT c.course_id, c.course_name, c.credits, c.description,
                   p.username AS professor_name,
                   (SELECT COUNT(*) FROM course_enrollment ce WHERE ce.course_id = c.course_id AND ce.status = 1) AS enrollment_count
            FROM course c
            JOIN sys_user p ON c.professor_id = p.user_id
            WHERE c.course_id = %s
        """
        course = execute_query(sql, (course_id,), fetch_one=True)
        if not course:
            return jsonify({"code": 404, "msg": "课程不存在", "data": None}), 404

        # 获取课程安排
        schedule_sql = """
            SELECT schedule_id, weekday, start_time, end_time, classroom
            FROM course_schedule
            WHERE course_id = %s
            ORDER BY weekday, start_time
        """
        schedules = execute_query(schedule_sql, (course_id,), fetch_all=True)
        for s in schedules:
            for time_field in ['start_time', 'end_time']:
                val = s.get(time_field)
                if val is not None:
                    if hasattr(val, 'isoformat'):
                        s[time_field] = val.isoformat()
                    else:
                        s[time_field] = str(val)
        course['schedules'] = schedules
        return jsonify({"code": 200, "msg": "success", "data": course})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


# ==================== 选课管理 ====================

def _check_time_conflict(student_id, course_id):
    """
    检查新课程是否与学生已选课程的时间冲突
    返回 (conflict, conflict_course_name)
    """
    # 获取新课程的所有安排
    new_schedules = execute_query(
        "SELECT weekday, start_time, end_time FROM course_schedule WHERE course_id = %s",
        (course_id,), fetch_all=True
    )
    if not new_schedules:
        return False, None  # 无安排，无冲突

    # 获取学生已选课程的所有安排（status=1）
    existing_sql = """
        SELECT cs.weekday, cs.start_time, cs.end_time, c.course_name
        FROM course_enrollment ce
        JOIN course_schedule cs ON ce.course_id = cs.course_id
        JOIN course c ON ce.course_id = c.course_id
        WHERE ce.student_id = %s AND ce.status = 1
    """
    existing_schedules = execute_query(existing_sql, (student_id,), fetch_all=True)

    # 时间重叠判断
    for new in new_schedules:
        new_start = new['start_time']
        new_end = new['end_time']
        for exist in existing_schedules:
            if exist['weekday'] != new['weekday']:
                continue
            # 区间重叠： (A_start < B_end) and (A_end > B_start)
            if new_start < exist['end_time'] and new_end > exist['start_time']:
                return True, exist['course_name']
    return False, None


@student_bp.route('/api/student/enroll', methods=['POST'])
@token_required
@role_required(0)
def enroll_course():
    """学生选课（含重复选课、时间冲突检测）"""
    try:
        student_id = request.user_id
        data = request.get_json()
        course_id = data.get('course_id')

        if not course_id:
            return jsonify({"code": 400, "msg": "缺少course_id", "data": None}), 400

        # 1. 检查课程是否存在
        course = execute_query(
            "SELECT course_id FROM course WHERE course_id = %s",
            (course_id,), fetch_one=True
        )
        if not course:
            return jsonify({"code": 404, "msg": "课程不存在", "data": None}), 404

        # 2. 检查是否已经选过（status=1）
        existing = execute_query(
            "SELECT enrollment_id FROM course_enrollment WHERE student_id = %s AND course_id = %s AND status = 1",
            (student_id, course_id), fetch_one=True
        )
        if existing:
            return jsonify({"code": 400, "msg": "您已经选过该课程", "data": None}), 400

        # 3. 时间冲突检测
        conflict, conflict_course = _check_time_conflict(student_id, course_id)
        if conflict:
            return jsonify({
                "code": 400,
                "msg": f"选课时间与已选课程「{conflict_course}」冲突",
                "data": None
            }), 400

        # 4. 插入选课记录
        execute_query(
            "INSERT INTO course_enrollment (student_id, course_id, status) VALUES (%s, %s, 1)",
            (student_id, course_id), commit=True
        )

        return jsonify({"code": 200, "msg": "选课成功", "data": {"course_id": course_id}})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@student_bp.route('/api/student/enroll/<int:enrollment_id>', methods=['DELETE'])
@token_required
@role_required(0)
def drop_course(enrollment_id):
    """退课（软删除，status改为3）"""
    try:
        student_id = request.user_id
        # 校验该选课记录属于当前学生且状态为在读
        record = execute_query(
            "SELECT enrollment_id FROM course_enrollment WHERE enrollment_id = %s AND student_id = %s AND status = 1",
            (enrollment_id, student_id), fetch_one=True
        )
        if not record:
            return jsonify({"code": 404, "msg": "选课记录不存在或已退课", "data": None}), 404

        execute_query(
            "UPDATE course_enrollment SET status = 3 WHERE enrollment_id = %s",
            (enrollment_id,), commit=True
        )
        return jsonify({"code": 200, "msg": "退课成功", "data": None})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@student_bp.route('/api/student/my-courses', methods=['GET'])
@token_required
@role_required(0)
def get_my_courses():
    """查看我的选课列表（在读课程）"""
    try:
        student_id = request.user_id
        sql = """
            SELECT ce.enrollment_id, c.course_id, c.course_name, c.credits,
                   p.username AS professor_name,
                   ce.enroll_time, ce.final_score
            FROM course_enrollment ce
            JOIN course c ON ce.course_id = c.course_id
            JOIN sys_user p ON c.professor_id = p.user_id
            WHERE ce.student_id = %s AND ce.status = 1
            ORDER BY ce.enroll_time DESC
        """
        courses = execute_query(sql, (student_id,), fetch_all=True)
        for c in courses:
            if hasattr(c['enroll_time'], 'isoformat'):
                c['enroll_time'] = c['enroll_time'].isoformat()
        return jsonify({"code": 200, "msg": "success", "data": courses})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


# ==================== 个人课程表（按周分组） ====================

def _weekday_to_str(weekday):
    """weekday数字转英文星期名"""
    mapping = {1: "Monday", 2: "Tuesday", 3: "Wednesday",
               4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}
    return mapping.get(weekday, "Unknown")


@student_bp.route('/api/student/schedule', methods=['GET'])
@token_required
@role_required(0)
def get_my_schedule():
    """
    获取个人课程表（按周显示，包含课程和活动）
    返回格式：
    {
        "Monday": [
            {
                "type": "course",
                "course_name": "魔药学",
                "start_time": "09:00:00",
                "end_time": "10:30:00",
                "classroom": "地下教室",
                "professor_name": "斯内普"
            },
            {
                "type": "activity",
                "activity_name": "Tea with Hagrid",
                "activity_name_cn": "去海格小屋喝茶",
                "start_time": "14:00:00",
                "end_time": "15:30:00",
                "location": "Hagrid's Hut",
                "is_time_turner": true
            }
        ],
        ...
    }
    """
    try:
        student_id = request.user_id

        # 1. 获取课程安排
        course_sql = """
            SELECT c.course_name, cs.weekday, cs.start_time, cs.end_time,
                   cs.classroom, p.username AS professor_name
            FROM course_enrollment ce
            JOIN course c ON ce.course_id = c.course_id
            JOIN course_schedule cs ON c.course_id = cs.course_id
            JOIN sys_user p ON c.professor_id = p.user_id
            WHERE ce.student_id = %s AND ce.status = 1
            ORDER BY cs.weekday, cs.start_time
        """
        courses = execute_query(course_sql, (student_id,), fetch_all=True)

        # 2. 获取活动安排（时间转换器活动）
        activity_sql = """
            SELECT a.activity_name, a.activity_name_cn, sae.weekday,
                   sae.start_time, sae.end_time, a.location
            FROM student_activity_enrollment sae
            JOIN activity a ON sae.activity_id = a.activity_id
            WHERE sae.student_id = %s AND sae.status = 1
            ORDER BY sae.weekday, sae.start_time
        """
        activities = execute_query(activity_sql, (student_id,), fetch_all=True)

        weekday_map = {1: "Monday", 2: "Tuesday", 3: "Wednesday",
                       4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}
        week_schedule = {day: [] for day in weekday_map.values()}

        # 3. 处理课程数据
        for s in courses:
            day = weekday_map.get(s['weekday'], "Monday")

            # 处理 start_time 和 end_time
            start = s['start_time']
            end = s['end_time']

            if hasattr(start, 'total_seconds'):
                start = str(start)
            elif hasattr(start, 'isoformat'):
                start = start.isoformat()
            else:
                start = str(start)

            if hasattr(end, 'total_seconds'):
                end = str(end)
            elif hasattr(end, 'isoformat'):
                end = end.isoformat()
            else:
                end = str(end)

            week_schedule[day].append({
                "type": "course",
                "course_name": s['course_name'],
                "start_time": start,
                "end_time": end,
                "classroom": s['classroom'] or "",
                "professor_name": s['professor_name']
            })

        # 4. 处理活动数据
        for a in activities:
            day = weekday_map.get(a['weekday'], "Monday")

            # 处理 start_time 和 end_time
            start = a['start_time']
            end = a['end_time']

            if hasattr(start, 'total_seconds'):
                start = str(start)
            elif hasattr(start, 'isoformat'):
                start = start.isoformat()
            else:
                start = str(start)

            if hasattr(end, 'total_seconds'):
                end = str(end)
            elif hasattr(end, 'isoformat'):
                end = end.isoformat()
            else:
                end = str(end)

            week_schedule[day].append({
                "type": "activity",
                "activity_name": a['activity_name'],
                "activity_name_cn": a['activity_name_cn'],
                "start_time": start,
                "end_time": end,
                "location": a['location'] or "",
                "is_time_turner": True  # 标记为时间转换器活动
            })

        # 5. 对每天的课程表按时间排序
        for day in week_schedule:
            week_schedule[day].sort(key=lambda x: x['start_time'])

        return jsonify({"code": 200, "msg": "success", "data": week_schedule})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


# ==================== 我的课堂表现记录 ====================

@student_bp.route('/api/student/my-performances', methods=['GET'])
@token_required
@role_required(0)
def get_my_performances():
    """
    查看我的课堂表现记录（关联积分变动）
    支持分页
    """
    try:
        student_id = request.user_id
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        offset = (page - 1) * limit

        # 总数
        count_sql = "SELECT COUNT(*) as total FROM class_performance WHERE student_id = %s"
        total = execute_query(count_sql, (student_id,), fetch_one=True)['total']

        sql = """
            SELECT cp.performance_id, cp.course_id, c.course_name,
                   cp.performance_type, cp.score, pl.reason, cp.create_time,
                   p.username AS professor_name
            FROM class_performance cp
            JOIN course c ON cp.course_id = c.course_id
            JOIN sys_user p ON cp.professor_id = p.user_id
            JOIN point_log pl ON cp.point_log_id = pl.log_id
            WHERE cp.student_id = %s
            ORDER BY cp.create_time DESC
            LIMIT %s OFFSET %s
        """
        performances = execute_query(sql, (student_id, limit, offset), fetch_all=True)
        for perf in performances:
            if hasattr(perf['create_time'], 'isoformat'):
                perf['create_time'] = perf['create_time'].isoformat()
            # performance_type 转文字
            type_map = {1: "回答问题", 2: "课堂作业", 3: "小组合作"}
            perf['performance_type_name'] = type_map.get(perf['performance_type'], "未知")

        return jsonify({
            "code": 200,
            "msg": "success",
            "data": {"performances": performances, "total": total, "page": page, "limit": limit}
        })
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


# ==================== 时间转换器功能 ====================

@student_bp.route('/api/student/time-turner/status', methods=['GET'])
@token_required
@role_required(0)
def get_time_turner_status():
    """
    查询学生是否拥有时间转换器
    返回格式：
    {
        "code": 200,
        "msg": "success",
        "data": {
            "has_time_turner": true/false,
            "house_name": "Gryffindor",
            "is_top_house": true/false,
            "house_rank": [...] // 所有学院排名
        }
    }
    """
    try:
        student_id = request.user_id

        # 检查学生是否拥有时间转换器
        has_time_turner, house_name, is_top_house = check_student_has_time_turner(student_id)

        # 获取学院排名信息
        house_rank = get_student_house_rank()

        # 格式化排名数据
        for house in house_rank:
            house['house_rank'] = int(house['house_rank'])

        return jsonify({
            "code": 200,
            "msg": "success",
            "data": {
                "has_time_turner": has_time_turner,
                "house_name": house_name,
                "is_top_house": is_top_house,
                "house_rank": house_rank
            }
        })
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@student_bp.route('/api/student/activities', methods=['GET'])
@token_required
@role_required(0)
def get_all_activities():
    """
    获取所有可用的活动列表
    只有拥有时间转换器的学生才能访问此接口
    返回格式：
    {
        "code": 200,
        "msg": "success",
        "data": [
            {
                "activity_id": 1,
                "activity_name": "Tea with Hagrid",
                "activity_name_cn": "去海格小屋喝茶",
                "location": "Hagrid's Hut",
                "description": "...",
                "suggested_duration": 90
            }
        ]
    }
    """
    try:
        student_id = request.user_id

        # 验证学生是否拥有时间转换器
        has_time_turner, _, _ = check_student_has_time_turner(student_id)
        if not has_time_turner:
            return jsonify({
                "code": 403,
                "msg": "您所在的学院不是第一名，无法使用时间转换器",
                "data": None
            }), 403

        # 获取所有启用的活动（不包含固定时间）
        sql = """
            SELECT activity_id, activity_name, activity_name_cn,
                   location, description, suggested_duration
            FROM activity
            WHERE status = 1
            ORDER BY activity_id
        """
        activities = execute_query(sql, fetch_all=True)

        return jsonify({
            "code": 200,
            "msg": "success",
            "data": activities
        })
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@student_bp.route('/api/student/my-activities', methods=['GET'])
@token_required
@role_required(0)
def get_my_activities():
    """
    获取我已选择的活动列表
    返回格式：
    {
        "code": 200,
        "msg": "success",
        "data": [
            {
                "enrollment_id": 1,
                "activity_id": 1,
                "activity_name": "Tea with Hagrid",
                "activity_name_cn": "去海格小屋喝茶",
                "weekday": 2,
                "start_time": "09:00:00",
                "end_time": "09:50:00",
                "location": "Hagrid's Hut",
                "enrolled_at": "2024-01-01T10:00:00",
                "status": 1
            }
        ]
    }
    """
    try:
        student_id = request.user_id

        sql = """
            SELECT sae.enrollment_id, sae.activity_id, sae.weekday,
                   sae.start_time, sae.end_time, sae.enrolled_at, sae.status,
                   a.activity_name, a.activity_name_cn, a.location, a.description
            FROM student_activity_enrollment sae
            JOIN activity a ON sae.activity_id = a.activity_id
            WHERE sae.student_id = %s AND sae.status = 1
            ORDER BY sae.weekday, sae.start_time
        """
        activities = execute_query(sql, (student_id,), fetch_all=True)

        # 格式化数据
        for activity in activities:
            # 处理时间字段
            for time_field in ['start_time', 'end_time']:
                val = activity.get(time_field)
                if val is not None:
                    if hasattr(val, 'total_seconds'):  # timedelta
                        activity[time_field] = str(val)
                    elif hasattr(val, 'isoformat'):  # time
                        activity[time_field] = val.isoformat()
                    else:
                        activity[time_field] = str(val)

            # 处理enrolled_at
            if hasattr(activity['enrolled_at'], 'isoformat'):
                activity['enrolled_at'] = activity['enrolled_at'].isoformat()

        return jsonify({
            "code": 200,
            "msg": "success",
            "data": activities
        })
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@student_bp.route('/api/student/activity/enroll', methods=['POST'])
@token_required
@role_required(0)
def enroll_activity():
    """
    选择活动（使用时间转换器）
    请求体：
    {
        "activity_id": 1,
        "weekday": 2,
        "start_time": "09:00:00",
        "end_time": "09:50:00"
    }
    返回格式：
    {
        "code": 200,
        "msg": "活动选择成功",
        "data": {
            "enrollment_id": 1,
            "activity_id": 1
        }
    }
    """
    try:
        student_id = request.user_id
        data = request.get_json()
        activity_id = data.get('activity_id')
        weekday = data.get('weekday')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        print(f"[时间转换器] 接收到的参数: activity_id={activity_id}, weekday={weekday}, start_time={start_time}, end_time={end_time}")

        # 验证必填参数
        if not activity_id:
            return jsonify({"code": 400, "msg": "缺少activity_id", "data": None}), 400
        if not weekday or not start_time or not end_time:
            return jsonify({"code": 400, "msg": "缺少时间参数（weekday, start_time, end_time）", "data": None}), 400

        # 1. 验证学生是否拥有时间转换器
        has_time_turner, house_name, _ = check_student_has_time_turner(student_id)
        if not has_time_turner:
            return jsonify({
                "code": 403,
                "msg": "您所在的学院不是第一名，无法使用时间转换器",
                "data": None
            }), 403

        # 2. 检查活动是否存在且启用
        activity = execute_query(
            "SELECT activity_id, activity_name_cn FROM activity WHERE activity_id = %s AND status = 1",
            (activity_id,), fetch_one=True
        )
        if not activity:
            return jsonify({"code": 404, "msg": "活动不存在或已禁用", "data": None}), 404

        # 3. 检查该时间段是否已经有活动安排
        if check_activity_already_enrolled_at_time(student_id, weekday, start_time, end_time):
            return jsonify({
                "code": 400,
                "msg": f"该时间段已经安排了活动",
                "data": None
            }), 400

        # 4. 检查该时间段是否有课程（时间转换器要求必须在有课时使用）
        has_course, course_info = check_time_slot_has_course(student_id, weekday, start_time, end_time)
        if not has_course:
            return jsonify({
                "code": 400,
                "msg": "时间转换器只能在有课程的时间使用，该时间段您没有课程安排",
                "data": None
            }), 400

        # 5. 插入活动选课记录（包含学生安排的时间）
        enrollment_id = execute_query(
            """
            INSERT INTO student_activity_enrollment 
            (student_id, activity_id, weekday, start_time, end_time, status) 
            VALUES (%s, %s, %s, %s, %s, 1)
            """,
            (student_id, activity_id, weekday, start_time, end_time), 
            commit=True, return_lastrowid=True
        )

        return jsonify({
            "code": 200,
            "msg": f"成功选择活动「{activity['activity_name_cn']}」",
            "data": {
                "enrollment_id": enrollment_id,
                "activity_id": activity_id
            }
        })
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@student_bp.route('/api/student/activity/enroll/<int:enrollment_id>', methods=['DELETE'])
@token_required
@role_required(0)
def cancel_activity(enrollment_id):
    """
    取消活动
    返回格式：
    {
        "code": 200,
        "msg": "活动取消成功",
        "data": None
    }
    """
    try:
        student_id = request.user_id

        # 验证该活动选课记录属于当前学生且状态有效
        record = execute_query(
            """
            SELECT sae.enrollment_id, a.activity_name_cn
            FROM student_activity_enrollment sae
            JOIN activity a ON sae.activity_id = a.activity_id
            WHERE sae.enrollment_id = %s AND sae.student_id = %s AND sae.status = 1
            """,
            (enrollment_id, student_id), fetch_one=True
        )

        if not record:
            return jsonify({
                "code": 404,
                "msg": "活动选课记录不存在或已取消",
                "data": None
            }), 404

        # 删除活动选课记录（软删除，状态改为0）
        execute_query(
            "UPDATE student_activity_enrollment SET status = 0 WHERE enrollment_id = %s",
            (enrollment_id,), commit=True
        )

        return jsonify({
            "code": 200,
            "msg": f"成功取消活动「{record['activity_name_cn']}」",
            "data": None
        })
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500