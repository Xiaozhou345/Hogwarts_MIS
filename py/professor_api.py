from flask import Blueprint, request, jsonify
from db_utils import execute_query
from auth_utils import token_required, role_required

professor_bp = Blueprint('professor', __name__)


@professor_bp.route('/api/students', methods=['GET'])
@token_required
@role_required(1)
def get_students():
    try:
        students = execute_query(
            "SELECT user_id, username, house_id FROM sys_user WHERE role = 0",
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

        student = execute_query(
            "SELECT user_id, role FROM sys_user WHERE user_id = %s AND role = 0",
            (student_id,),
            fetch_one=True
        )
        if not student:
            return jsonify({"code": 400, "msg": "学生不存在", "data": None}), 400

        execute_query(
            "INSERT INTO point_log (student_id, professor_id, score_change, reason) VALUES (%s, %s, %s, %s)",
            (student_id, request.user_id, score_change, reason),
            commit=True
        )

        return jsonify({"code": 200, "msg": "积分工单提交成功", "data": None})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@professor_bp.route('/api/professor/logs', methods=['GET'])
@token_required
@role_required(1)
def get_professor_logs():
    try:
        logs = execute_query(
            """SELECT pl.log_id, su.username AS student_name, pl.score_change, pl.reason, pl.create_time
               FROM point_log pl
               JOIN sys_user su ON pl.student_id = su.user_id
               WHERE pl.professor_id = %s
               ORDER BY pl.create_time DESC""",
            (request.user_id,),
            fetch_all=True
        )

        for log in logs:
            if hasattr(log['create_time'], 'isoformat'):
                log['create_time'] = log['create_time'].isoformat()

        return jsonify({"code": 200, "msg": "success", "data": logs})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500
