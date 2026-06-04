import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'py'))

from db_utils import execute_query

print('=' * 50)
print('课程安排检查')
print('=' * 50)

# 查询所有课程
courses = execute_query('SELECT course_id, course_name, professor_id FROM course', fetch_all=True)
print('\n所有课程：')
for c in courses:
    print(f'  ID={c["course_id"]}, 名称="{c["course_name"]}"')
    
    # 查询该课程的安排
    schedules = execute_query(
        'SELECT COUNT(*) as count FROM course_schedule WHERE course_id = %s',
        (c['course_id'],),
        fetch_one=True
    )
    print(f'    课程安排数量：{schedules["count"]}')

# 查询学生的选课
print('\n学生选课情况（学生ID=1）：')
enrollments = execute_query(
    'SELECT ce.enrollment_id, c.course_name, ce.status FROM course_enrollment ce JOIN course c ON ce.course_id = c.course_id WHERE ce.student_id = %s',
    (1,),
    fetch_all=True
)
for e in enrollments:
    status_text = '已选课' if e['status'] == 1 else '已退课'
    print(f'  {e["course_name"]} - {status_text}')

print('=' * 50)