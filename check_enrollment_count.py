import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'py'))

from db_utils import execute_query

print('=' * 60)
print('选课人数统计检查')
print('=' * 60)

# 1. 查询所有学生
print('\n【所有学生】')
students = execute_query(
    "SELECT user_id, username FROM sys_user WHERE role = 0",
    fetch_all=True
)
for s in students:
    print(f'  学生ID={s["user_id"]}, 用户名="{s["username"]}"')

# 2. 查询所有课程
print('\n【所有课程】')
courses = execute_query(
    "SELECT course_id, course_name FROM course",
    fetch_all=True
)
for c in courses:
    print(f'  课程ID={c["course_id"]}, 名称="{c["course_name"]}"')
    
    # 查询该课程的选课人数
    count = execute_query(
        "SELECT COUNT(*) as count FROM course_enrollment WHERE course_id = %s AND status = 1",
        (c['course_id'],),
        fetch_one=True
    )
    print(f'    选课人数：{count["count"]}')

# 3. 查询所有选课记录
print('\n【所有选课记录】')
enrollments = execute_query(
    '''
    SELECT u.username as student_name, c.course_name, ce.status
    FROM course_enrollment ce
    JOIN sys_user u ON ce.student_id = u.user_id
    JOIN course c ON ce.course_id = c.course_id
    ORDER BY c.course_name, u.username
    ''',
    fetch_all=True
)
for e in enrollments:
    status_text = '已选课' if e['status'] == 1 else '已退课'
    print(f'  {e["student_name"]} - {e["course_name"]} ({status_text})')

print('=' * 60)