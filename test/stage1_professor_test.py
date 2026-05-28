import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'py'))
import requests
import json
import time
from db_utils import execute_query

BASE_URL = "http://127.0.0.1:5000/api"

TIMESTAMP = str(int(time.time()))
TEST_PROFESSOR = f"test_prof_{TIMESTAMP}"
TEST_STUDENT = f"test_stu_{TIMESTAMP}"
TEST_PASSWORD = "test123456"


def print_test_header(test_name):
    print("\n" + "=" * 60)
    print(f"[TEST] {test_name}")
    print("=" * 60)


def print_result(response):
    print(f"状态码: {response.status_code}")
    try:
        data = response.json()
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    except Exception:
        print(f"响应: {response.text}")


_professor_token = None
_student_id = None


def _register_and_login_professor():
    global _professor_token
    data = {
        "username": TEST_PROFESSOR,
        "password": TEST_PASSWORD,
        "role": 1,
        "house_id": None
    }
    requests.post(f"{BASE_URL}/register", json=data)

    resp = requests.post(f"{BASE_URL}/login", json={
        "username": TEST_PROFESSOR,
        "password": TEST_PASSWORD
    })
    if resp.status_code == 200:
        _professor_token = resp.json()["data"]["token"]
    return _professor_token


def _register_student():
    global _student_id
    data = {
        "username": TEST_STUDENT,
        "password": TEST_PASSWORD,
        "role": 0,
        "house_id": 1
    }
    resp = requests.post(f"{BASE_URL}/register", json=data)
    if resp.status_code == 200:
        login_resp = requests.post(f"{BASE_URL}/login", json={
            "username": TEST_STUDENT,
            "password": TEST_PASSWORD
        })
        if login_resp.status_code == 200:
            _student_id = login_resp.json()["data"]["user_id"]
    return _student_id


def test_get_students():
    print_test_header("获取学生下拉列表")
    _register_and_login_professor()
    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}
        response = requests.get(f"{BASE_URL}/students", headers=headers)
        print_result(response)
        if response.status_code == 200:
            students = response.json().get("data", [])
            print(f"\n学生总数: {len(students)}")
            for s in students:
                print(f"  - {s['username']} (ID: {s['user_id']}, 学院: {s['house_id']})")
        return response.status_code == 200
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_submit_points_add():
    print_test_header("教授提交加分工单")
    _register_and_login_professor()
    _register_student()
    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}
        data = {
            "student_id": _student_id,
            "score_change": 20,
            "reason": "魔药课完美配置福灵剂"
        }
        response = requests.post(f"{BASE_URL}/points", json=data, headers=headers)
        print_result(response)
        return response.status_code == 200
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_submit_points_deduct():
    print_test_header("教授提交扣分工单")
    _register_and_login_professor()
    _register_student()
    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}
        data = {
            "student_id": _student_id,
            "score_change": -5,
            "reason": "上课迟到"
        }
        response = requests.post(f"{BASE_URL}/points", json=data, headers=headers)
        print_result(response)
        return response.status_code == 200
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_trigger_house_points():
    print_test_header("触发器验证：直接查库检查学院总分是否自动更新")
    _register_and_login_professor()
    _register_student()

    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}

        before = execute_query(
            "SELECT total_points FROM house WHERE house_id = 1",
            fetch_one=True
        )
        before_points = before['total_points'] if before else 0
        print(f"格兰芬多加分前总分: {before_points}")

        add_data = {
            "student_id": _student_id,
            "score_change": 50,
            "reason": "触发器测试-课堂表现优秀"
        }
        add_resp = requests.post(f"{BASE_URL}/points", json=add_data, headers=headers)
        if add_resp.status_code != 200:
            print("[FAIL] 加分提交失败")
            return False
        print(f"[OK] 提交 +50 分工单成功")

        time.sleep(0.5)

        after = execute_query(
            "SELECT total_points FROM house WHERE house_id = 1",
            fetch_one=True
        )
        after_points = after['total_points'] if after else 0
        print(f"格兰芬多加分后总分: {after_points}")
        print(f"变动差值: {after_points - before_points}")

        if after_points == before_points + 50:
            print("[OK] 触发器工作正常！学院总分自动更新了 +50")
            return True
        else:
            print(f"[FAIL] 触发器可能未生效！预期 {before_points + 50}，实际 {after_points}")
            return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_get_professor_logs():
    print_test_header("获取教授操作历史")
    _register_and_login_professor()
    _register_student()

    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}

        requests.post(f"{BASE_URL}/points", json={
            "student_id": _student_id,
            "score_change": 10,
            "reason": "测试日志-回答正确"
        }, headers=headers)

        response = requests.get(f"{BASE_URL}/professor/logs", headers=headers)
        print_result(response)

        if response.status_code == 200:
            data = response.json().get("data", {})
            logs = data.get("logs", [])
            total = data.get("total", len(logs))
            print(f"\n操作记录总数: {total}")
            for log in logs[:5]:
                print(f"  - [{log['create_time']}] {log['student_name']}: {log['score_change']:+d} ({log['reason']})")
        return response.status_code == 200
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_unauthorized_student_access():
    print_test_header("权限验证：学生Token访问教授接口（应该失败）")
    _register_student()
    try:
        login_resp = requests.post(f"{BASE_URL}/login", json={
            "username": TEST_STUDENT,
            "password": TEST_PASSWORD
        })
        if login_resp.status_code != 200:
            print("[FAIL] 学生登录失败")
            return False
        student_token = login_resp.json()["data"]["token"]

        headers = {"Authorization": f"Bearer {student_token}"}
        response = requests.get(f"{BASE_URL}/students", headers=headers)
        print_result(response)

        return response.status_code == 403
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def run_stage1_professor_tests():
    print("\n" + "=" * 60)
    print("霍格沃茨 MIS - 阶段一测试套件 [教授端业务写入]（组员3 余雨航）")
    print("=" * 60)

    results = []

    results.append(("获取学生列表", test_get_students()))
    results.append(("提交加分工单", test_submit_points_add()))
    results.append(("提交扣分工单", test_submit_points_deduct()))
    results.append(("触发器自动更新学院总分", test_trigger_house_points()))
    results.append(("获取教授操作历史", test_get_professor_logs()))
    results.append(("权限验证(学生越权)", test_unauthorized_student_access()))

    print("\n" + "=" * 60)
    print("阶段一[教授端]测试结果汇总")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print("\n" + "-" * 60)
    print(f"总计: {passed + failed} 个测试")
    print(f"[PASS]: {passed}")
    print(f"[FAIL]: {failed}")
    print(f"通过率: {passed / (passed + failed) * 100:.1f}%" if passed + failed > 0 else "N/A")
    print("-" * 60 + "\n")

    if failed == 0:
        print("恭喜！阶段一[教授端]所有测试通过！\n")
    else:
        print("[WARN] 部分测试失败，请检查代码。\n")

    return passed, failed


if __name__ == "__main__":
    print("[WARN] 请先启动 Flask 应用，然后运行此测试脚本。")
    print("启动命令: python py/app.py\n")
