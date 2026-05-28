import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'py'))
import requests
import json
import time
from db_utils import execute_query

BASE_URL = "http://127.0.0.1:5000/api"

TIMESTAMP = str(int(time.time()))
TEST_PROFESSOR = f"test_s2prof_{TIMESTAMP}"
TEST_STUDENT = f"test_s2stu_{TIMESTAMP}"
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
    if _professor_token:
        return _professor_token
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
    if _student_id:
        return _student_id
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


def test_student_list_with_house_name():
    print_test_header("获取学生列表（含学院名称）")
    _register_and_login_professor()
    _register_student()
    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}
        response = requests.get(f"{BASE_URL}/students", headers=headers)
        print_result(response)
        if response.status_code == 200:
            students = response.json().get("data", [])
            print(f"\n学生总数: {len(students)}")
            has_house_name = True
            for s in students:
                if 'house_name' not in s:
                    has_house_name = False
                    print(f"  [WARN] {s['username']} 缺少 house_name 字段")
                else:
                    print(f"  - {s['username']} (ID: {s['user_id']}, 学院: {s['house_name']})")
            if not has_house_name:
                print("[FAIL] 部分学生缺少 house_name 字段")
            return has_house_name
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_submit_points_with_validation():
    print_test_header("提交积分工单：正常范围加分为 20 分")
    _register_and_login_professor()
    _register_student()
    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}
        data = {
            "student_id": _student_id,
            "score_change": 20,
            "reason": "课堂表现优秀回答问题"
        }
        response = requests.post(f"{BASE_URL}/points", json=data, headers=headers)
        print_result(response)
        if response.status_code == 200:
            resp_data = response.json().get("data", {})
            if resp_data.get("student_id") == _student_id and resp_data.get("score_change") == 20:
                print(f"[OK] 返回数据正确：student_id={resp_data['student_id']}, score_change={resp_data['score_change']}")
                return True
            else:
                print(f"[FAIL] 返回数据不正确")
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_score_exceeds_max():
    print_test_header("边界校验：单次加分超过 +100（应该失败）")
    _register_and_login_professor()
    _register_student()
    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}
        data = {
            "student_id": _student_id,
            "score_change": 150,
            "reason": "试图超额加分"
        }
        response = requests.post(f"{BASE_URL}/points", json=data, headers=headers)
        print_result(response)
        expected = (response.status_code == 400 and "100" in response.json().get("msg", ""))
        if expected:
            print("[OK] 系统正确拦截了超额加分请求")
        else:
            print("[FAIL] 系统未能正确拦截超额加分请求")
        return expected
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_score_exceeds_min():
    print_test_header("边界校验：单次扣分超过 -100（应该失败）")
    _register_and_login_professor()
    _register_student()
    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}
        data = {
            "student_id": _student_id,
            "score_change": -101,
            "reason": "试图超额扣分"
        }
        response = requests.post(f"{BASE_URL}/points", json=data, headers=headers)
        print_result(response)
        expected = (response.status_code == 400 and "100" in response.json().get("msg", ""))
        if expected:
            print("[OK] 系统正确拦截了超额扣分请求")
        else:
            print("[FAIL] 系统未能正确拦截超额扣分请求")
        return expected
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_empty_reason():
    print_test_header("参数校验：事由为空（应该失败）")
    _register_and_login_professor()
    _register_student()
    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}
        data = {
            "student_id": _student_id,
            "score_change": 10,
            "reason": "   "
        }
        response = requests.post(f"{BASE_URL}/points", json=data, headers=headers)
        print_result(response)
        expected = response.status_code == 400
        if expected:
            print("[OK] 系统正确拦截了空事由请求")
        else:
            print("[FAIL] 系统未能正确拦截空事由请求")
        return expected
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_reason_too_long():
    print_test_header("参数校验：事由超过 200 字符（应该失败）")
    _register_and_login_professor()
    _register_student()
    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}
        data = {
            "student_id": _student_id,
            "score_change": 5,
            "reason": "测" * 201
        }
        response = requests.post(f"{BASE_URL}/points", json=data, headers=headers)
        print_result(response)
        expected = response.status_code == 400
        if expected:
            print("[OK] 系统正确拦截了超长事由请求")
        else:
            print("[FAIL] 系统未能正确拦截超长事由请求")
        return expected
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_professor_logs_pagination():
    print_test_header("教授操作历史：分页功能验证")
    _register_and_login_professor()
    _register_student()

    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}

        for i in range(3):
            requests.post(f"{BASE_URL}/points", json={
                "student_id": _student_id,
                "score_change": 5,
                "reason": f"分页测试-第{i+1}条"
            }, headers=headers)

        response = requests.get(f"{BASE_URL}/professor/logs?page=1&limit=2", headers=headers)
        print_result(response)

        if response.status_code == 200:
            data = response.json().get("data", {})
            logs = data.get("logs", [])
            total = data.get("total", 0)
            page = data.get("page", 0)
            limit = data.get("limit", 0)

            print(f"\n分页信息: page={page}, limit={limit}, total={total}")
            print(f"返回记录数: {len(logs)}")

            if limit == 2 and len(logs) <= 2 and total >= 3 and page == 1:
                print("[OK] 分页功能正常")
                return True
            else:
                print(f"[FAIL] 分页信息不正确")
                return False
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_professor_logs_total_count():
    print_test_header("教授操作历史：总条数验证")
    _register_and_login_professor()
    _register_student()

    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}

        db_before = execute_query(
            "SELECT COUNT(*) AS cnt FROM point_log WHERE professor_id = (SELECT user_id FROM sys_user WHERE username = %s)",
            (TEST_PROFESSOR,),
            fetch_one=True
        )
        before_count = db_before['cnt'] if db_before else 0

        requests.post(f"{BASE_URL}/points", json={
            "student_id": _student_id,
            "score_change": 3,
            "reason": "总数测试"
        }, headers=headers)

        response = requests.get(f"{BASE_URL}/professor/logs", headers=headers)

        if response.status_code == 200:
            data = response.json().get("data", {})
            api_total = data.get("total", 0)

            db_after = execute_query(
                "SELECT COUNT(*) AS cnt FROM point_log WHERE professor_id = (SELECT user_id FROM sys_user WHERE username = %s)",
                (TEST_PROFESSOR,),
                fetch_one=True
            )
            db_total = db_after['cnt'] if db_after else 0

            print(f"API 返回 total: {api_total}")
            print(f"数据库实际总数: {db_total}")

            if api_total == db_total:
                print("[OK] total 计数与数据库一致")
                return True
            else:
                print("[FAIL] total 计数与数据库不一致")
                return False
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_trigger_integration():
    print_test_header("触发器集成验证：加分后学院总分正确更新")
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

        resp = requests.post(f"{BASE_URL}/points", json={
            "student_id": _student_id,
            "score_change": 15,
            "reason": "触发器集成测试"
        }, headers=headers)

        if resp.status_code != 200:
            print(f"[FAIL] 提交工单失败")
            return False

        time.sleep(0.5)

        after = execute_query(
            "SELECT total_points FROM house WHERE house_id = 1",
            fetch_one=True
        )
        after_points = after['total_points'] if after else 0
        print(f"格兰芬多加分后总分: {after_points}")
        print(f"变动差值: {after_points - before_points}")

        if after_points == before_points + 15:
            print("[OK] 触发器正常，学院总分自动更新")
            return True
        else:
            print(f"[FAIL] 触发器异常：预期 {before_points + 15}，实际 {after_points}")
            return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def run_stage2_professor_tests():
    print("\n" + "=" * 60)
    print("霍格沃茨 MIS - 阶段二测试套件 [教授端完善]（组员3 余雨航）")
    print("=" * 60)

    results = []

    results.append(("学生列表含学院名称", test_student_list_with_house_name()))
    results.append(("正常提交积分工单", test_submit_points_with_validation()))
    results.append(("超额加分拦截", test_score_exceeds_max()))
    results.append(("超额扣分拦截", test_score_exceeds_min()))
    results.append(("空事由拦截", test_empty_reason()))
    results.append(("超长事由拦截", test_reason_too_long()))
    results.append(("操作历史分页", test_professor_logs_pagination()))
    results.append(("操作历史总数验证", test_professor_logs_total_count()))
    results.append(("触发器集成验证", test_trigger_integration()))

    print("\n" + "=" * 60)
    print("阶段二[教授端]测试结果汇总")
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

    total = passed + failed
    print("\n" + "-" * 60)
    print(f"总计: {total} 个测试")
    print(f"[PASS]: {passed}")
    print(f"[FAIL]: {failed}")
    print(f"通过率: {passed / total * 100:.1f}%" if total > 0 else "N/A")
    print("-" * 60 + "\n")

    if failed == 0:
        print("恭喜！阶段二[教授端]所有测试通过！\n")
    else:
        print("[WARN] 部分测试失败，请检查代码。\n")

    return passed, failed


if __name__ == "__main__":
    print("[WARN] 请先启动 Flask 应用，然后运行此测试脚本。")
    print("启动命令: python py/app.py\n")
