import sys
import os

file_path = os.path.join(os.path.dirname(__file__), 'py', 'student_api.py')

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 替换字段名
content = content.replace('AS \nenrolled_count', 'AS enrollment_count')
content = content.replace('AS enrolled_count', 'AS enrollment_count')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ 字段名修改完成')
print('已将 enrolled_count 改为 enrollment_count')