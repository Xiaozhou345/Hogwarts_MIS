import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'py'))

from db_utils import execute_query

print('=' * 60)
print('课程安排详细检查')
print('=' * 60)

# 查询所有课程
print('\n【所有课程】')
courses = execute_query('SELECT course_id, course_name FROM course', fetch_all=True)
for c in courses:
    print(f'  课程ID={c["course_id"]}, 名称="{c["course_name"]}"')

# 查询所有课程安排
print('\n【所有课程安排】')
schedules = execute_query(
    '''
    SELECT cs.schedule_id, cs.course_id, c.course_name, cs.weekday, 
           cs.start_time, cs.end_time, cs.classroom
    FROM course_schedule cs
    JOIN course c ON cs.course_id = c.course_id
    ORDER BY cs.weekday, cs.start_time
    ''',
    fetch_all=True
)

weekday_map = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}

for s in schedules:
    day = weekday_map.get(s['weekday'], f'周{s["weekday"]}')
    start = str(s['start_time'])
    end = str(s['end_time'])
    print(f'  安排ID={s["schedule_id"]}, 课程ID={s["course_id"]}, 课程="{s["course_name"]}"')
    print(f'    时间：{day} {start}-{end}, 教室：{s["classroom"]}')

# 查询学生的课程表（学生ID=1）
print('\n【学生课程表（学生ID=1）】')
student_schedule = execute_query(
    '''
    SELECT c.course_id, c.course_name, cs.weekday, cs.start_time, cs.end_time,
           cs.classroom, p.username AS professor_name
    FROM course_enrollment ce
    JOIN course c ON ce.course_id = c.course_id
    JOIN course_schedule cs ON c.course_id = cs.course_id
    JOIN sys_user p ON c.professor_id = p.user_id
    WHERE ce.student_id = %s AND ce.status = 1
    ORDER BY cs.weekday, cs.start_time
    ''',
    (1,),
    fetch_all=True
)

for s in student_schedule:
    day = weekday_map.get(s['weekday'], f'周{s["weekday"]}')
    start = str(s['start_time'])
    end = str(s['end_time'])
    print(f'  课程ID={s["course_id"]}, 课程="{s["course_name"]}"')
    print(f'    时间：{day} {start}-{end}, 教室：{s["classroom"]}, 教授：{s["professor_name"]}')

print('=' * 60)