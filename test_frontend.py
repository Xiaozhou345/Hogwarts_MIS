import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_flow():
    print("=" * 60)
    print("前端联调测试脚本")
    print("=" * 60)
    
    print("\n【步骤1】测试教授登录")
    login_res = requests.post(f"{BASE_URL}/login", json={
        "username": "Snape",
        "password": "123456"
    })
    print(f"状态码: {login_res.status_code}")
    login_data = login_res.json()
    print(f"响应: {json.dumps(login_data, indent=2, ensure_ascii=False)}")
    
    if login_data['code'] != 200:
        print("❌ 教授登录失败，请先注册 Snape 账号")
        return
    
    professor_token = login_data['data']['token']
    professor_id = login_data['data']['user_id']
    print(f"✅ 教授登录成功，user_id={professor_id}")
    
    print("\n【步骤2】获取学生列表")
    students_res = requests.get(f"{BASE_URL}/students", headers={
        "Authorization": f"Bearer {professor_token}"
    })
    print(f"状态码: {students_res.status_code}")
    students_data = students_res.json()
    print(f"响应: {json.dumps(students_data, indent=2, ensure_ascii=False)}")
    
    if not students_data['data']:
        print("❌ 没有学生数据，请先注册学生账号")
        return
    
    harry = None
    for student in students_data['data']:
        if student['username'] == 'Harry':
            harry = student
            break
    
    if not harry:
        print("❌ 没有找到 Harry，请先注册 Harry 账号")
        return
    
    print(f"✅ 找到 Harry，user_id={harry['user_id']}")
    
    print("\n【步骤3】测试学生登录")
    student_login_res = requests.post(f"{BASE_URL}/login", json={
        "username": "Harry",
        "password": "123456"
    })
    student_login_data = student_login_res.json()
    print(f"响应: {json.dumps(student_login_data, indent=2, ensure_ascii=False)}")
    
    if student_login_data['code'] != 200:
        print("❌ 学生登录失败")
        return
    
    student_token = student_login_data['data']['token']
    student_user_id = student_login_data['data']['user_id']
    print(f"✅ 学生登录成功，user_id={student_user_id}")
    
    print("\n【步骤4】查询学生个人信息")
    info_res = requests.get(f"{BASE_URL}/student/info", headers={
        "Authorization": f"Bearer {student_token}"
    })
    print(f"状态码: {info_res.status_code}")
    info_data = info_res.json()
    print(f"响应: {json.dumps(info_data, indent=2, ensure_ascii=False)}")
    
    if info_data['code'] == 200:
        print(f"✅ 学生信息查询成功")
    
    print("\n【步骤5】查询学生积分流水")
    logs_res = requests.get(f"{BASE_URL}/student/logs", headers={
        "Authorization": f"Bearer {student_token}"
    })
    print(f"状态码: {logs_res.status_code}")
    logs_data = logs_res.json()
    print(f"响应: {json.dumps(logs_data, indent=2, ensure_ascii=False)}")
    
    if logs_data['code'] == 200:
        if logs_data['data']:
            print(f"✅ 找到 {len(logs_data['data'])} 条积分记录")
            for log in logs_data['data']:
                score_text = f"+{log['score_change']}" if log['score_change'] > 0 else str(log['score_change'])
                print(f"   - {log['professor_name']}: {score_text} ({log['reason']})")
        else:
            print("⚠️  没有积分记录，请先在教授端提交工单")
    
    print("\n【步骤6】查询教授操作历史")
    professor_logs_res = requests.get(f"{BASE_URL}/professor/logs", headers={
        "Authorization": f"Bearer {professor_token}"
    })
    print(f"状态码: {professor_logs_res.status_code}")
    professor_logs_data = professor_logs_res.json()
    print(f"响应: {json.dumps(professor_logs_data, indent=2, ensure_ascii=False)}")
    
    if professor_logs_data['code'] == 200:
        if professor_logs_data['data']:
            print(f"✅ 找到 {len(professor_logs_data['data'])} 条操作记录")
        else:
            print("⚠️  没有操作记录")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_flow()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("请确认后端服务已启动: cd py && python app.py")
