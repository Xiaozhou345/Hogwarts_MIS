import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'py'))

from db_utils import execute_query

print('=' * 60)
print('修复课程安排')
print('=' * 60)

# 1. 查看当前情况
print('\n【当前情况】')
schedules = execute_query(
    '''
    SELECT cs.schedule_id, c.course_name, cs.weekday, cs.start_time, cs.classroom
    FROM course_schedule cs
    JOIN course c ON cs.course_id = c.course_id
    ORDER BY cs.weekday, cs.start_time
    ''',
    fetch_all=True
)

weekday_map = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}

for s in schedules:
    day = weekday_map.get(s['weekday'], f'周{s["weekday"]}')
    print(f'  安排ID={s["schedule_id"]}: {day} {s["start_time"]} - {s["course_name"]} @ {s["classroom"]}')

# 2. 执行修复
print('\n【执行修复】')
print('  将周二15:00和周四10:00的安排改为黑魔法防御术...')

execute_query(
    'UPDATE course_schedule SET course_id = 4 WHERE schedule_id IN (8, 7)',
    commit=True
)

print('  ✅ 修复完成')

# 3. 查看修复后的情况
print('\n【修复后情况】')
schedules = execute_query(
    '''
    SELECT cs.schedule_id, c.course_name, cs.weekday, cs.start_time, cs.classroom
    FROM course_schedule cs
    JOIN course c ON cs.course_id = c.course_id
    ORDER BY cs.weekday, cs.start_time
    ''',
    fetch_all=True
)

for s in schedules:
    day = weekday_map.get(s['weekday'], f'周{s["weekday"]}')
    print(f'  安排ID={s["schedule_id"]}: {day} {s["start_time"]} - {s["course_name"]} @ {s["classroom"]}')

print('=' * 60)
print('修复完成！请刷新浏览器查看效果')
print('=' * 60)