import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'py'))

from db_utils import execute_query

sql = """
    SELECT c.course_id, c.course_name, cs.weekday, cs.start_time, cs.end_time,
           cs.classroom, p.username AS professor_name
    FROM course_enrollment ce
    JOIN course c ON ce.course_id = c.course_id
    JOIN course_schedule cs ON c.course_id = cs.course_id
    JOIN sys_user p ON c.professor_id = p.user_id
    WHERE ce.student_id = %s AND ce.status = 1
    ORDER BY cs.weekday, cs.start_time
"""
schedules = execute_query(sql, (1,), fetch_all=True)
print('课程表数据:')
for s in schedules:
    print(s)