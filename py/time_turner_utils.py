# time_turner_utils.py - 时间转换器相关工具函数
from db_utils import execute_query


def get_top_house_id():
    """
    获取当前积分排名第一的学院ID
    :return: 学院ID，如果没有学院则返回None
    """
    sql = """
        SELECT house_id, total_points
        FROM house
        ORDER BY total_points DESC
        LIMIT 1
    """
    result = execute_query(sql, fetch_one=True)
    return result['house_id'] if result else None


def check_student_has_time_turner(student_id):
    """
    检查学生是否拥有时间转换器
    规则：只有积分排名第一的学院的学生才拥有时间转换器

    :param student_id: 学生ID
    :return: (has_time_turner, house_name, is_top_house)
             - has_time_turner: 布尔值，是否拥有时间转换器
             - house_name: 学院名称
             - is_top_house: 是否是第一名学院
    """
    # 获取学生所属学院
    student_sql = """
        SELECT u.house_id, h.house_name, h.total_points
        FROM sys_user u
        LEFT JOIN house h ON u.house_id = h.house_id
        WHERE u.user_id = %s AND u.role = 0
    """
    student = execute_query(student_sql, (student_id,), fetch_one=True)

    if not student or not student['house_id']:
        return False, None, False

    # 获取第一名学院ID
    top_house_id = get_top_house_id()

    if not top_house_id:
        return False, student['house_name'], False

    # 判断学生所属学院是否是第一名
    is_top_house = (student['house_id'] == top_house_id)

    return is_top_house, student['house_name'], is_top_house


def check_time_slot_has_course(student_id, weekday, start_time, end_time):
    """
    检查学生在指定时间段是否有课程
    时间转换器要求：必须在有课的时间才能使用

    :param student_id: 学生ID
    :param weekday: 星期 1-7
    :param start_time: 开始时间
    :param end_time: 结束时间
    :return: (has_course, course_info)
             - has_course: 是否有课（True表示有课，可以使用时间转换器）
             - course_info: 课程信息
    """
    # 获取学生在该时间段的课程
    course_sql = """
        SELECT c.course_name, cs.start_time, cs.end_time, cs.classroom
        FROM course_enrollment ce
        JOIN course c ON ce.course_id = c.course_id
        JOIN course_schedule cs ON c.course_id = cs.course_id
        WHERE ce.student_id = %s
        AND ce.status = 1
        AND cs.weekday = %s
        AND cs.start_time < %s
        AND cs.end_time > %s
    """
    conflicting_courses = execute_query(
        course_sql,
        (student_id, weekday, end_time, start_time),
        fetch_all=True
    )

    # 时间转换器的逻辑：必须在有课的时间才能使用
    if conflicting_courses:
        return True, conflicting_courses
    else:
        return False, None


def check_activity_already_enrolled_at_time(student_id, weekday, start_time, end_time):
    """
    检查学生在指定时间段是否已经安排了活动

    :param student_id: 学生ID
    :param weekday: 星期 1-7
    :param start_time: 开始时间
    :param end_time: 结束时间
    :return: 布尔值，True表示已安排
    """
    sql = """
        SELECT enrollment_id
        FROM student_activity_enrollment
        WHERE student_id = %s 
        AND weekday = %s 
        AND start_time = %s 
        AND end_time = %s 
        AND status = 1
    """
    result = execute_query(sql, (student_id, weekday, start_time, end_time), fetch_one=True)
    return result is not None


def get_student_house_rank():
    """
    获取所有学院的排名信息
    :return: 学院排名列表
    """
    sql = """
        SELECT house_id, house_name, total_points,
               RANK() OVER (ORDER BY total_points DESC) as house_rank
        FROM house
        ORDER BY total_points DESC
    """
    return execute_query(sql, fetch_all=True)
