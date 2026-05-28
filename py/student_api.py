# student_api.py - 学生端个人中心 API
# student_api.py - 学生端个人中心 API（第二阶段）
from flask import Blueprint, jsonify, request
from db_utils import execute_query
from auth_utils import token_required, role_required

student_bp = Blueprint('student', __name__)


@student_bp.route('/api/student/info', methods=['GET'])
@token_required
@role_required(0)
def get_student_info():
    """
    学生个人信息查询
    返回：username, house_name, total_points
    """
    try:
        user_id = request.user_id

        sql = """
            SELECT u.username, h.house_name, h.total_points
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
    """
    学生积分变动明细
    返回：logs列表，包含积分变动、事由、操作教授、时间
    """
    try:
        user_id = request.user_id

        sql = """
            SELECT pl.log_id, pl.score_change, pl.reason, pl.create_time,
                   p.username AS professor_name
            FROM point_log pl
            JOIN sys_user p ON pl.professor_id = p.user_id
            WHERE pl.student_id = %s
            ORDER BY pl.create_time DESC
        """
        logs = execute_query(sql, (user_id,), fetch_all=True)

        for log in logs:
            if hasattr(log['create_time'], 'isoformat'):
                log['create_time'] = log['create_time'].isoformat()

        return jsonify({"code": 200, "msg": "success", "data": logs})

    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500