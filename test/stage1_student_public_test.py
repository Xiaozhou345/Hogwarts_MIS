import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000/api"

TIMESTAMP = str(int(time.time()))
TEST_STUDENT = f"test_student_{TIMESTAMP}"
TEST_PROFESSOR = f"test_professor_{TIMESTAMP}"
STUDENT_PASSWORD = "test123456"
PROFESSOR_PASSWORD = "prof123456"

def print_test_header(test_name):
    print("\n" + "="*60)
    print(f"[TEST] {test_name}")
    print("="*60)

def print_result(response):
    print(f"状态码: {response.status_code}")
    try:
        data = response.json()
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    except:
        print(f"响应: {response.text}")

def setup_test_data():
    """准备测试数据：注册学生和教授，教授给学生加分"""
    print_test_header("准备测试数据")

    # 注册学生
    student_data = {
        "username": TEST_STUDENT,
        "password": STUDENT_PASSWORD,
        "role": 0,
        "house_id": 1
    }
    requests.post(f"{BASE_URL}/register", json=student_data)

    # 注册教授
    professor_data = {
        "username": TEST_PROFESSOR,
        "password": PROFESSOR_PASSWORD,
        "role": 1,
        "house_id": None
    }
    requests.post(f"{BASE_URL}/register", json=professor_data)

    # 学生登录获取 token
    login_response = requests.post(f"{BASE_URL}/login", json={
        "username": TEST_STUDENT,
        "password": STUDENT_PASSWORD
    })
    student_token = login_response.json()['data']['token']
    student_id = login_response.json()['data']['user_id']

    # 教授登录获取 token
    login_response = requests.post(f"{BASE_URL}/login", json={
        "username": TEST_PROFESSOR,
        "password": PROFESSOR_PASSWORD
    })
    professor_token = login_response.json()['data']['token']

    # 教授给学生加分
    headers = {"Authorization": f"Bearer {professor_token}"}
    requests.post(f"{BASE_URL}/points", json={
        "student_id": student_id,
        "score_change": 20,
        "reason": "课堂表现优秀"
    }, headers=headers)

    requests.post(f"{BASE_URL}/points", json={
        "student_id": student_id,
        "score_change": -5,
        "reason": "作业迟交"
    }, headers=headers)

    print("[OK] 测试数据准备完成")
    return student_token, professor_token, student_id

def test_student_info(student_token):
    """测试获取学生个人信息"""
    print_test_header("获取学生个人信息")
    try:
        headers = {"Authorization": f"Bearer {student_token}"}
        response = requests.get(f"{BASE_URL}/student/info", headers=headers)
        print_result(response)

        if response.status_code == 200:
            data = response.json()['data']
            print(f"\n学生信息:")
            print(f"  - 用户名: {data['username']}")
            print(f"  - 学院: {data['house_name']} (ID: {data['house_id']})")
            return True
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False

def test_student_logs(student_token):
    """测试获取学生积分流水"""
    print_test_header("获取学生积分流水")
    try:
        headers = {"Authorization": f"Bearer {student_token}"}
        response = requests.get(f"{BASE_URL}/student/logs", headers=headers)
        print_result(response)

        if response.status_code == 200:
            data = response.json()['data']
            logs = data['logs']
            print(f"\n积分记录总数: {data['total']}")
            for log in logs:
                score = f"+{log['score_change']}" if log['score_change'] > 0 else str(log['score_change'])
                print(f"  - [{log['create_time']}] {log['professor_name']}: {score} ({log['reason']})")
            return True
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False

def test_student_logs_pagination(student_token):
    """测试学生积分流水分页"""
    print_test_header("学生积分流水分页测试")
    try:
        headers = {"Authorization": f"Bearer {student_token}"}
        response = requests.get(f"{BASE_URL}/student/logs?page=1&limit=1", headers=headers)
        print_result(response)

        if response.status_code == 200:
            data = response.json()['data']
            print(f"\n[OK] 分页参数: page={data['page']}, limit={data['limit']}")
            print(f"[OK] 返回记录数: {len(data['logs'])}")
            return len(data['logs']) == 1
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False

def test_house_ranking():
    """测试学院排行榜（公开接口）"""
    print_test_header("学院排行榜查询")
    try:
        response = requests.get(f"{BASE_URL}/house/ranking")
        print_result(response)

        if response.status_code == 200:
            data = response.json()['data']
            print(f"\n学院排行榜:")
            for i, house in enumerate(data, 1):
                print(f"  {i}. {house['house_name']}: {house['total_points']} 分")
            return True
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False

def test_public_logs():
    """测试全校积分动态（公开接口）"""
    print_test_header("全校最新积分动态")
    try:
        response = requests.get(f"{BASE_URL}/public/logs")
        print_result(response)

        if response.status_code == 200:
            data = response.json()['data']
            print(f"\n最新动态 (共 {len(data)} 条):")
            for log in data[:5]:  # 只显示前5条
                score = f"+{log['score_change']}" if log['score_change'] > 0 else str(log['score_change'])
                print(f"  - {log['student_name']} 被 {log['professor_name']} {score} 分: {log['reason']}")
            return True
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False

def test_public_logs_limit():
    """测试全校积分动态限制条数"""
    print_test_header("全校积分动态限制条数测试")
    try:
        response = requests.get(f"{BASE_URL}/public/logs?limit=3")
        print_result(response)

        if response.status_code == 200:
            data = response.json()['data']
            print(f"\n[OK] 请求 limit=3，返回 {len(data)} 条记录")
            return len(data) <= 3
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False

def test_professor_access_student_api(professor_token):
    """测试教授访问学生接口（应该失败）"""
    print_test_header("权限验证：教授访问学生接口（应该失败）")
    try:
        headers = {"Authorization": f"Bearer {professor_token}"}
        response = requests.get(f"{BASE_URL}/student/info", headers=headers)
        print_result(response)
        return response.status_code == 403
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False

def run_stage1_student_public_tests():
    """运行学生端和公共模块测试"""
    print("\n" + "="*60)
    print("霍格沃茨 MIS - 阶段一测试套件 [学生端+公共]（组员4 费翔鸿）")
    print("="*60)

    results = []

    # 准备测试数据
    student_token, professor_token, student_id = setup_test_data()

    # 学生端测试
    results.append(("获取学生个人信息", test_student_info(student_token)))
    results.append(("获取学生积分流水", test_student_logs(student_token)))
    results.append(("学生积分流水分页", test_student_logs_pagination(student_token)))

    # 公共模块测试
    results.append(("学院排行榜查询", test_house_ranking()))
    results.append(("全校积分动态", test_public_logs()))
    results.append(("积分动态限制条数", test_public_logs_limit()))

    # 权限验证
    results.append(("权限验证(教授越权)", test_professor_access_student_api(professor_token)))

    print("\n" + "="*60)
    print("阶段一[学生端+公共]测试结果汇总")
    print("="*60)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print("\n" + "-"*60)
    print(f"总计: {passed + failed} 个测试")
    print(f"[PASS]: {passed}")
    print(f"[FAIL]: {failed}")
    print(f"通过率: {passed/(passed+failed)*100:.1f}%")
    print("-"*60 + "\n")

    if failed == 0:
        print("恭喜！阶段一[学生端+公共]所有测试通过！\n")
    else:
        print("[WARN] 部分测试失败，请检查代码。\n")

    return passed, failed

if __name__ == "__main__":
    print("[WARN] 请先启动 Flask 应用，然后运行此测试脚本。")
    print("启动命令: python py/app.py")
    print("\n或者设置 TEST_MODE=true 自动运行测试\n")
