# student_api.py - 学生端个人中心 API
from flask import Blueprint, jsonify, request
from db_utils import execute_query
from auth_utils import token_required, role_required

student_bp = Blueprint('student', __name__)


@student_bp.route('/api/student/info', methods=['GET'])
@token_required
@role_required(0)   # 只允许学生访问
def get_student_info():
    """
    个人信息查询：联合 sys_user 和 house 表，返回学生的姓名和学院信息
    请求头需带 Token
    """
    try:
        user_id = request.user_id   # 从 token 中获取

        sql = """
            SELECT u.user_id, u.username, u.role, 
                   h.house_id, h.house_name
            FROM sys_user u
            LEFT JOIN house h ON u.house_id = h.house_id
            WHERE u.user_id = %s AND u.role = 0
        """
        result = execute_query(sql, (user_id,), fetch_one=True)

        if not result:
            return jsonify({"code": 404, "msg": "学生不存在", "data": None}), 404

        return jsonify({"code": 200, "msg": "success", "data": result})

    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@student_bp.route('/api/student/logs', methods=['GET'])
@token_required
@role_required(0)
def get_student_points_logs():
    """
    学生积分通知：根据学生 ID，查询 point_log 明细（加减分明细）
    支持分页参数 ?page=1&limit=10（可选）
    """
    try:
        user_id = request.user_id
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        offset = (page - 1) * limit

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

        # 处理时间格式（转换为字符串）
        for log in logs:
            if hasattr(log['create_time'], 'isoformat'):
                log['create_time'] = log['create_time'].isoformat()

        # 同时获取总数（用于分页）
        count_sql = "SELECT COUNT(*) as total FROM point_log WHERE student_id = %s"
        total = execute_query(count_sql, (user_id,), fetch_one=True)['total']

        return jsonify({
            "code": 200,
            "msg": "success",
            "data": {
                "logs": logs,
                "total": total,
                "page": page,
                "limit": limit
            }
        })

    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500