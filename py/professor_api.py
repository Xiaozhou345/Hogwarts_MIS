from flask import Blueprint, request, jsonify
from db_utils import execute_query
from auth_utils import token_required, role_required

professor_bp = Blueprint('professor', __name__)

MAX_SCORE_CHANGE = 100
MAX_REASON_LENGTH = 200


@professor_bp.route('/api/students', methods=['GET'])
@token_required
@role_required(1)
def get_students():
    try:
        students = execute_query(
            """SELECT u.user_id, u.username, u.house_id, h.house_name
               FROM sys_user u
               LEFT JOIN house h ON u.house_id = h.house_id
               WHERE u.role = 0
               ORDER BY u.user_id""",
            fetch_all=True
        )
        return jsonify({"code": 200, "msg": "success", "data": students})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@professor_bp.route('/api/points', methods=['POST'])
@token_required
@role_required(1)
def submit_points():
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        score_change = data.get('score_change')
        reason = data.get('reason')

        if not student_id or score_change is None or not reason:
            return jsonify({"code": 400, "msg": "缺少必要参数(student_id, score_change, reason)", "data": None}), 400

        if not isinstance(score_change, int) or score_change == 0:
            return jsonify({"code": 400, "msg": "score_change 必须为非零整数", "data": None}), 400

        if abs(score_change) > MAX_SCORE_CHANGE:
            return jsonify({"code": 400, "msg": f"单次分数变动不能超过 ±{MAX_SCORE_CHANGE} 分", "data": None}), 400

        reason = reason.strip()
        if not reason or len(reason) > MAX_REASON_LENGTH:
            return jsonify({"code": 400, "msg": f"事由不能为空且长度不能超过 {MAX_REASON_LENGTH} 字符", "data": None}), 400

        student = execute_query(
            "SELECT u.user_id, u.role, u.house_id FROM sys_user u WHERE u.user_id = %s AND u.role = 0",
            (student_id,),
            fetch_one=True
        )
        if not student:
            return jsonify({"code": 400, "msg": "学生不存在", "data": None}), 400

        if student.get('house_id') is None:
            return jsonify({"code": 400, "msg": "该学生未分配学院，无法提交积分工单", "data": None}), 400

        execute_query(
            "INSERT INTO point_log (student_id, professor_id, score_change, reason) VALUES (%s, %s, %s, %s)",
            (student_id, request.user_id, score_change, reason),
            commit=True
        )

        return jsonify({"code": 200, "msg": "积分工单提交成功", "data": {
            "student_id": student_id,
            "score_change": score_change,
            "reason": reason
        }})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@professor_bp.route('/api/professor/logs', methods=['GET'])
@token_required
@role_required(1)
def get_professor_logs():
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        if limit > 100:
            limit = 100
        offset = (page - 1) * limit

        count_result = execute_query(
            "SELECT COUNT(*) AS total FROM point_log WHERE professor_id = %s",
            (request.user_id,),
            fetch_one=True
        )
        total = count_result['total'] if count_result else 0

        logs = execute_query(
            """SELECT pl.log_id, su.username AS student_name, pl.score_change, pl.reason, pl.create_time
               FROM point_log pl
               JOIN sys_user su ON pl.student_id = su.user_id
               WHERE pl.professor_id = %s
               ORDER BY pl.create_time DESC
               LIMIT %s OFFSET %s""",
            (request.user_id, limit, offset),
            fetch_all=True
        )

        for log in logs:
            if hasattr(log['create_time'], 'isoformat'):
                log['create_time'] = log['create_time'].isoformat()

        return jsonify({"code": 200, "msg": "success", "data": {
            "logs": logs,
            "total": total,
            "page": page,
            "limit": limit
        }})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@professor_bp.route('/api/professor/courses', methods=['GET'])
@token_required
@role_required(1)
def get_professor_courses():
    try:
        courses = execute_query(
            """SELECT c.course_id, c.course_name, c.credits, c.description,
                      (SELECT COUNT(*) FROM course_enrollment ce WHERE ce.course_id = c.course_id AND ce.status = 1) AS enrollment_count
               FROM course c
               WHERE c.professor_id = %s
               ORDER BY c.course_id DESC""",
            (request.user_id,),
            fetch_all=True
        )
        return jsonify({"code": 200, "msg": "success", "data": courses})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@professor_bp.route('/api/professor/course', methods=['POST'])
@token_required
@role_required(1)
def create_course():
    try:
        data = request.get_json()
        course_name = data.get('course_name', '').strip()
        credits = data.get('credits', 2)
        description = data.get('description', '').strip()

        if not course_name:
            return jsonify({"code": 400, "msg": "课程名称不能为空", "data": None}), 400

        if not isinstance(credits, int) or credits < 1 or credits > 10:
            return jsonify({"code": 400, "msg": "学分必须为 1-10 之间的整数", "data": None}), 400

        course_id = execute_query(
            "INSERT INTO course (course_name, professor_id, credits, description) VALUES (%s, %s, %s, %s)",
            (course_name, request.user_id, credits, description),
            commit=True,
            return_lastrowid=True
        )

        return jsonify({"code": 200, "msg": "课程创建成功", "data": {
            "course_id": course_id,
            "course_name": course_name,
            "professor_id": request.user_id,
            "credits": credits,
            "description": description
        }})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@professor_bp.route('/api/professor/course/<int:course_id>', methods=['PUT'])
@token_required
@role_required(1)
def update_course(course_id):
    try:
        course = execute_query(
            "SELECT * FROM course WHERE course_id = %s AND professor_id = %s",
            (course_id, request.user_id),
            fetch_one=True
        )
        if not course:
            return jsonify({"code": 403, "msg": "课程不存在或无权操作", "data": None}), 403

        data = request.get_json()
        course_name = data.get('course_name', '').strip()
        credits = data.get('credits')
        description = data.get('description', '').strip()

        if not course_name:
            return jsonify({"code": 400, "msg": "课程名称不能为空", "data": None}), 400

        if credits is not None and (not isinstance(credits, int) or credits < 1 or credits > 10):
            return jsonify({"code": 400, "msg": "学分必须为 1-10 之间的整数", "data": None}), 400

        execute_query(
            "UPDATE course SET course_name = %s, credits = %s, description = %s WHERE course_id = %s",
            (course_name, credits if credits else course['credits'], description, course_id),
            commit=True
        )

        return jsonify({"code": 200, "msg": "课程更新成功", "data": {
            "course_id": course_id,
            "course_name": course_name,
            "credits": credits if credits else course['credits'],
            "description": description
        }})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@professor_bp.route('/api/professor/course/<int:course_id>', methods=['DELETE'])
@token_required
@role_required(1)
def delete_course(course_id):
    try:
        course = execute_query(
            "SELECT * FROM course WHERE course_id = %s AND professor_id = %s",
            (course_id, request.user_id),
            fetch_one=True
        )
        if not course:
            return jsonify({"code": 403, "msg": "课程不存在或无权操作", "data": None}), 403

        execute_query("DELETE FROM course_enrollment WHERE course_id = %s", (course_id,), commit=True)
        execute_query("DELETE FROM class_performance WHERE course_id = %s", (course_id,), commit=True)
        execute_query("DELETE FROM course_schedule WHERE course_id = %s", (course_id,), commit=True)
        execute_query("DELETE FROM course WHERE course_id = %s", (course_id,), commit=True)

        return jsonify({"code": 200, "msg": "课程删除成功", "data": None})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@professor_bp.route('/api/professor/course/<int:course_id>/schedule', methods=['POST'])
@token_required
@role_required(1)
def add_course_schedule(course_id):
    try:
        course = execute_query(
            "SELECT * FROM course WHERE course_id = %s AND professor_id = %s",
            (course_id, request.user_id),
            fetch_one=True
        )
        if not course:
            return jsonify({"code": 403, "msg": "课程不存在或无权操作", "data": None}), 403

        data = request.get_json()
        weekday = data.get('weekday')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        classroom = data.get('classroom', '').strip()

        if not weekday or not start_time or not end_time:
            return jsonify({"code": 400, "msg": "缺少必要参数(weekday, start_time, end_time)", "data": None}), 400

        if not isinstance(weekday, int) or weekday < 1 or weekday > 7:
            return jsonify({"code": 400, "msg": "weekday 必须为 1-7 的整数", "data": None}), 400

        schedule_id = execute_query(
            "INSERT INTO course_schedule (course_id, weekday, start_time, end_time, classroom) VALUES (%s, %s, %s, %s, %s)",
            (course_id, weekday, start_time, end_time, classroom),
            commit=True,
            return_lastrowid=True
        )

        return jsonify({"code": 200, "msg": "课程安排添加成功", "data": {
            "schedule_id": schedule_id,
            "course_id": course_id,
            "weekday": weekday,
            "start_time": start_time,
            "end_time": end_time,
            "classroom": classroom
        }})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@professor_bp.route('/api/professor/course/<int:course_id>/schedule', methods=['GET'])
@token_required
@role_required(1)
def get_course_schedule(course_id):
    try:
        schedules = execute_query(
            "SELECT schedule_id, course_id, weekday, start_time, end_time, classroom FROM course_schedule WHERE course_id = %s ORDER BY weekday, start_time",
            (course_id,),
            fetch_all=True
        )
        for s in schedules:
            for time_field in ['start_time', 'end_time']:
                val = s.get(time_field)
                if val is not None:
                    if hasattr(val, 'isoformat'):
                        s[time_field] = val.isoformat()
                    else:
                        s[time_field] = str(val)
        return jsonify({"code": 200, "msg": "success", "data": schedules})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@professor_bp.route('/api/professor/schedule/<int:schedule_id>', methods=['DELETE'])
@token_required
@role_required(1)
def delete_course_schedule(schedule_id):
    try:
        schedule = execute_query(
            "SELECT cs.* FROM course_schedule cs JOIN course c ON cs.course_id = c.course_id WHERE cs.schedule_id = %s AND c.professor_id = %s",
            (schedule_id, request.user_id),
            fetch_one=True
        )
        if not schedule:
            return jsonify({"code": 403, "msg": "课程安排不存在或无权操作", "data": None}), 403

        execute_query("DELETE FROM course_schedule WHERE schedule_id = %s", (schedule_id,), commit=True)
        return jsonify({"code": 200, "msg": "课程安排删除成功", "data": None})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@professor_bp.route('/api/professor/course/<int:course_id>/students', methods=['GET'])
@token_required
@role_required(1)
def get_course_students(course_id):
    try:
        course = execute_query(
            "SELECT * FROM course WHERE course_id = %s AND professor_id = %s",
            (course_id, request.user_id),
            fetch_one=True
        )
        if not course:
            return jsonify({"code": 403, "msg": "课程不存在或无权操作", "data": None}), 403

        students = execute_query(
            """SELECT ce.enrollment_id, u.user_id AS student_id, u.username AS student_name,
                      h.house_name, ce.enroll_time, ce.status
               FROM course_enrollment ce
               JOIN sys_user u ON ce.student_id = u.user_id
               LEFT JOIN house h ON u.house_id = h.house_id
               WHERE ce.course_id = %s AND ce.status = 1
               ORDER BY ce.enroll_time""",
            (course_id,),
            fetch_all=True
        )
        for s in students:
            if hasattr(s['enroll_time'], 'isoformat'):
                s['enroll_time'] = s['enroll_time'].isoformat()
        return jsonify({"code": 200, "msg": "success", "data": students})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@professor_bp.route('/api/professor/class-performance', methods=['POST'])
@token_required
@role_required(1)
def record_class_performance():
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        course_id = data.get('course_id')
        performance_type = data.get('performance_type')
        score = data.get('score')
        reason = data.get('reason', '').strip()

        if not student_id or not course_id or performance_type is None or score is None:
            return jsonify({"code": 400, "msg": "缺少必要参数(student_id, course_id, performance_type, score)", "data": None}), 400

        if not isinstance(score, int) or score == 0:
            return jsonify({"code": 400, "msg": "score 必须为非零整数", "data": None}), 400

        if abs(score) > MAX_SCORE_CHANGE:
            return jsonify({"code": 400, "msg": f"单次分数变动不能超过 ±{MAX_SCORE_CHANGE} 分", "data": None}), 400

        if performance_type not in (1, 2, 3):
            return jsonify({"code": 400, "msg": "performance_type 必须为 1(回答问题)、2(课堂作业) 或 3(小组合作)", "data": None}), 400

        if not reason:
            return jsonify({"code": 400, "msg": "事由不能为空", "data": None}), 400

        if len(reason) > MAX_REASON_LENGTH:
            return jsonify({"code": 400, "msg": f"事由长度不能超过 {MAX_REASON_LENGTH} 字符", "data": None}), 400

        enrollment = execute_query(
            "SELECT * FROM course_enrollment WHERE student_id = %s AND course_id = %s AND status = 1",
            (student_id, course_id),
            fetch_one=True
        )
        if not enrollment:
            return jsonify({"code": 400, "msg": "该学生未选修此课程", "data": None}), 400

        course = execute_query(
            "SELECT * FROM course WHERE course_id = %s AND professor_id = %s",
            (course_id, request.user_id),
            fetch_one=True
        )
        if not course:
            return jsonify({"code": 403, "msg": "课程不存在或无权操作", "data": None}), 403

        point_log_id = execute_query(
            "INSERT INTO point_log (student_id, professor_id, score_change, reason) VALUES (%s, %s, %s, %s)",
            (student_id, request.user_id, score, reason),
            commit=True,
            return_lastrowid=True
        )

        performance_id = execute_query(
            """INSERT INTO class_performance (student_id, course_id, professor_id, performance_type, score, point_log_id)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (student_id, course_id, request.user_id, performance_type, score, point_log_id),
            commit=True,
            return_lastrowid=True
        )

        return jsonify({"code": 200, "msg": "课堂表现记录成功", "data": {
            "performance_id": performance_id,
            "point_log_id": point_log_id
        }})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@professor_bp.route('/api/professor/course/<int:course_id>/performances', methods=['GET'])
@token_required
@role_required(1)
def get_course_performances(course_id):
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        if limit > 100:
            limit = 100
        offset = (page - 1) * limit

        course = execute_query(
            "SELECT * FROM course WHERE course_id = %s AND professor_id = %s",
            (course_id, request.user_id),
            fetch_one=True
        )
        if not course:
            return jsonify({"code": 403, "msg": "课程不存在或无权操作", "data": None}), 403

        count_result = execute_query(
            "SELECT COUNT(*) AS total FROM class_performance WHERE course_id = %s",
            (course_id,),
            fetch_one=True
        )
        total = count_result['total'] if count_result else 0

        performances = execute_query(
            """SELECT cp.performance_id, u.username AS student_name, cp.performance_type,
                      cp.score, pl.reason, cp.create_time
               FROM class_performance cp
               JOIN sys_user u ON cp.student_id = u.user_id
               JOIN point_log pl ON cp.point_log_id = pl.log_id
               WHERE cp.course_id = %s
               ORDER BY cp.create_time DESC
               LIMIT %s OFFSET %s""",
            (course_id, limit, offset),
            fetch_all=True
        )

        for p in performances:
            if hasattr(p['create_time'], 'isoformat'):
                p['create_time'] = p['create_time'].isoformat()

        return jsonify({"code": 200, "msg": "success", "data": {
            "performances": performances,
            "total": total,
            "page": page,
            "limit": limit
        }})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500
