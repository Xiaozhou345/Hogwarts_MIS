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
