# public_api.py - 学院杯大厅公共展示 API（无需登录或仅需公开）
from flask import Blueprint, jsonify, request
from db_utils import execute_query

public_bp = Blueprint('public', __name__)


@public_bp.route('/api/house/ranking', methods=['GET'])
def get_house_ranking():
    """
    排行榜查询：按 total_points 降序返回四个学院的数据
    无需 token，公开接口
    """
    try:
        sql = """
            SELECT house_id, house_name, founder, total_points
            FROM house
            ORDER BY total_points DESC
        """
        ranking = execute_query(sql, fetch_all=True)

        return jsonify({"code": 200, "msg": "success", "data": ranking})

    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@public_bp.route('/api/public/logs', methods=['GET'])
def get_recent_dynamics():
    """
    全校最新动态：查询 point_log 表，按 create_time 倒序，LIMIT 10
    联合查询出学生姓名、教授姓名、分数变动、事由
    无需 token
    """
    try:
        # 支持通过 query 参数动态调整条数，默认 10
        limit = request.args.get('limit', 10, type=int)
        if limit > 50:
            limit = 50   # 限制最大50条

        sql = """
            SELECT pl.log_id, pl.score_change, pl.reason, pl.create_time,
                   s.username AS student_name,
                   p.username AS professor_name
            FROM point_log pl
            JOIN sys_user s ON pl.student_id = s.user_id
            JOIN sys_user p ON pl.professor_id = p.user_id
            ORDER BY pl.create_time DESC
            LIMIT %s
        """
        dynamics = execute_query(sql, (limit,), fetch_all=True)

        # 格式化时间
        for d in dynamics:
            if hasattr(d['create_time'], 'isoformat'):
                d['create_time'] = d['create_time'].isoformat()

        return jsonify({"code": 200, "msg": "success", "data": dynamics})

    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500