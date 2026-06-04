import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'py'))

from db_utils import execute_query

print("=" * 50)
print("课程表API测试")
print("=" * 50)

try:
    print("\n1. 检查数据库表...")
    tables = execute_query('SHOW TABLES', fetch_all=True)
    table_names = [list(t.values())[0] for t in tables]
    print(f"   找到 {len(table_names)} 个表：{', '.join(table_names)}")
    
    print("\n2. 检查 course_schedule 表...")
    if 'course_schedule' in table_names:
        schedules = execute_query('SELECT COUNT(*) as count FROM course_schedule', fetch_one=True)
        print(f"   课程安排数量：{schedules['count']}")
    else:
        print("   ❌ course_schedule 表不存在！")
    
    print("\n3. 检查 course_enrollment 表...")
    if 'course_enrollment' in table_names:
        enrollments = execute_query('SELECT COUNT(*) as count FROM course_enrollment WHERE status=1', fetch_one=True)
        print(f"   有效选课记录数量：{enrollments['count']}")
    else:
        print("   ❌ course_enrollment 表不存在！")
    
    print("\n4. 测试课程表查询（学生ID=1）...")
    sql = """
        SELECT c.course_name, cs.weekday, cs.start_time, cs.end_time,
               cs.classroom, p.username AS professor_name
        FROM course_enrollment ce
        JOIN course c ON ce.course_id = c.course_id
        JOIN course_schedule cs ON c.course_id = cs.course_id
        JOIN sys_user p ON c.professor_id = p.user_id
        WHERE ce.student_id = %s AND ce.status = 1
        ORDER BY cs.weekday, cs.start_time
    """
    schedules = execute_query(sql, (1,), fetch_all=True)
    print(f"   查询结果：找到 {len(schedules)} 条课程安排")
    
    if schedules:
        print("\n   课程安排详情：")
        for s in schedules:
            print(f"   - {s['course_name']}: 周{s['weekday']} {s['start_time']}-{s['end_time']}")
    else:
        print("   ⚠️  该学生还没有选课或课程没有安排时间")
    
    print("\n" + "=" * 50)
    print("✅ 测试完成！API查询正常")
    print("=" * 50)
    
except Exception as e:
    print("\n" + "=" * 50)
    print(f"❌ 错误：{str(e)}")
    print("=" * 50)
    import traceback
    traceback.print_exc()