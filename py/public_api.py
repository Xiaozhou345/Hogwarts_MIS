# public_api.py - 公共展示 API（无需登录）
from flask import Blueprint, jsonify, request
from db_utils import execute_query

public_bp = Blueprint('public', __name__)


# ==================== 原有接口（保留） ====================

@public_bp.route('/api/house/ranking', methods=['GET'])
def get_house_ranking():
    """学院排行榜（公开）"""
    try:
        ranking = execute_query(
            "SELECT house_id, house_name, founder, total_points FROM house ORDER BY total_points DESC",
            fetch_all=True
        )
        return jsonify({"code": 200, "msg": "success", "data": ranking})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@public_bp.route('/api/public/logs', methods=['GET'])
def get_recent_dynamics():
    """全校最新动态（公开）"""
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)
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
        for d in dynamics:
            if hasattr(d['create_time'], 'isoformat'):
                d['create_time'] = d['create_time'].isoformat()
        return jsonify({"code": 200, "msg": "success", "data": dynamics})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


# ==================== 第三阶段新增：课程公共接口 ====================

@public_bp.route('/api/public/courses', methods=['GET'])
def get_all_courses():
    """所有课程列表（公开，含教授名、选课人数）"""
    try:
        sql = """
            SELECT c.course_id, c.course_name, c.credits, c.description,
                   p.username AS professor_name,
                   (SELECT COUNT(*) FROM course_enrollment ce WHERE ce.course_id = c.course_id AND ce.status = 1) AS enrolled_count
            FROM course c
            JOIN sys_user p ON c.professor_id = p.user_id
            ORDER BY c.course_id
        """
        courses = execute_query(sql, fetch_all=True)
        return jsonify({"code": 200, "msg": "success", "data": courses})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@public_bp.route('/api/public/courses/popular', methods=['GET'])
def get_popular_courses():
    """热门课程排行（按选课人数降序，默认前10）"""
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)
        sql = """
            SELECT c.course_id, c.course_name, c.credits, p.username AS professor_name,
                   COUNT(ce.enrollment_id) AS enrolled_count
            FROM course c
            JOIN sys_user p ON c.professor_id = p.user_id
            LEFT JOIN course_enrollment ce ON c.course_id = ce.course_id AND ce.status = 1
            GROUP BY c.course_id
            ORDER BY enrolled_count DESC
            LIMIT %s
        """
        courses = execute_query(sql, (limit,), fetch_all=True)
        return jsonify({"code": 200, "msg": "success", "data": courses})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500


@public_bp.route('/api/public/courses/house-stats', methods=['GET'])
def get_course_house_stats():
    """
    学院课程统计：返回各学院在各门课程的平均分（基于 final_score）
    返回格式: [
        {"house_name": "Gryffindor", "course_name": "魔药学", "avg_score": 85.5},
        ...
    ]
    """
    try:
        sql = """
            SELECT h.house_name, c.course_name, AVG(ce.final_score) AS avg_score
            FROM course_enrollment ce
            JOIN sys_user u ON ce.student_id = u.user_id
            JOIN house h ON u.house_id = h.house_id
            JOIN course c ON ce.course_id = c.course_id
            WHERE ce.status = 1 AND ce.final_score IS NOT NULL
            GROUP BY h.house_id, c.course_id
            ORDER BY h.house_id, c.course_id
        """
        stats = execute_query(sql, fetch_all=True)
        # 处理 Decimal 类型转换为 float
        for s in stats:
            if s['avg_score'] is not None:
                s['avg_score'] = float(s['avg_score'])
        return jsonify({"code": 200, "msg": "success", "data": stats})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500