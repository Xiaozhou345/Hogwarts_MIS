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

def test_database_connection():
    print_test_header("数据库连接测试")
    try:
        response = requests.get(f"{BASE_URL}/test_db")
        print_result(response)
        return response.status_code == 200
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False

def test_register_student():
    print_test_header("学生注册测试")
    try:
        data = {
            "username": TEST_STUDENT,
            "password": STUDENT_PASSWORD,
            "role": 0,
            "house_id": 1
        }
        response = requests.post(f"{BASE_URL}/register", json=data)
        print_result(response)
        return response.status_code == 200
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False

def test_register_professor():
    print_test_header("教授注册测试")
    try:
        data = {
            "username": TEST_PROFESSOR,
            "password": PROFESSOR_PASSWORD,
            "role": 1,
            "house_id": None
        }
        response = requests.post(f"{BASE_URL}/register", json=data)
        print_result(response)
        return response.status_code == 200
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False

def test_register_duplicate():
    print_test_header("重复用户名注册测试（应该失败）")
    try:
        data = {
            "username": TEST_STUDENT,
            "password": "another_password",
            "role": 0,
            "house_id": 1
        }
        response = requests.post(f"{BASE_URL}/register", json=data)
        print_result(response)
        return response.status_code == 400 and "已存在" in response.json().get("msg", "")
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False

def test_login_student():
    print_test_header("学生登录测试")
    try:
        data = {
            "username": TEST_STUDENT,
            "password": STUDENT_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/login", json=data)
        print_result(response)

        if response.status_code == 200:
            result = response.json()
            token = result['data']['token']
            role = result['data']['role']
            print(f"\n[OK] 获取到 Token: {token[:50]}...")
            print(f"[OK] 用户角色: {'学生' if role == 0 else '教授'}")
            return True, token
        return False, None
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False, None

def test_login_professor():
    print_test_header("教授登录测试")
    try:
        data = {
            "username": TEST_PROFESSOR,
            "password": PROFESSOR_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/login", json=data)
        print_result(response)

        if response.status_code == 200:
            result = response.json()
            token = result['data']['token']
            role = result['data']['role']
            print(f"\n[OK] 获取到 Token: {token[:50]}...")
            print(f"[OK] 用户角色: {'学生' if role == 0 else '教授'}")
            return True, token
        return False, None
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False, None

def test_login_wrong_password():
    print_test_header("错误密码登录测试（应该失败）")
    try:
        data = {
            "username": TEST_STUDENT,
            "password": "wrong_password"
        }
        response = requests.post(f"{BASE_URL}/login", json=data)
        print_result(response)
        return response.status_code == 400
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False

def test_logout(token):
    print_test_header("登出测试")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/logout", headers=headers)
        print_result(response)
        return response.status_code == 200
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False

def run_stage1_tests():
    print("\n" + "="*60)
    print("霍格沃茨 MIS - 阶段一测试套件 [鉴权]（组员2 Noa）")
    print("="*60)

    results = []

    results.append(("数据库连接", test_database_connection()))
    results.append(("学生注册", test_register_student()))
    results.append(("教授注册", test_register_professor()))
    results.append(("重复用户名检测", test_register_duplicate()))

    success, student_token = test_login_student()
    results.append(("学生登录", success))

    success, professor_token = test_login_professor()
    results.append(("教授登录", success))

    results.append(("错误密码检测", test_login_wrong_password()))

    if student_token:
        results.append(("登出功能", test_logout(student_token)))

    print("\n" + "="*60)
    print("测试结果汇总")
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
        print("恭喜！阶段一[鉴权]所有测试通过！\n")
    else:
        print("[WARN] 部分测试失败，请检查代码。\n")

    return passed, failed


if __name__ == "__main__":
    print("[WARN] 请先启动 Flask 应用，然后运行此测试脚本。")
    print("启动命令: python py/app.py")
    print("\n或者设置 TEST_MODE=true 自动运行测试\n")
