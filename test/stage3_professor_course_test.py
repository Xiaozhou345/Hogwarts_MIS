import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'py'))
import requests
import json
import time
from db_utils import execute_query

BASE_URL = "http://127.0.0.1:5000/api"

TIMESTAMP = str(int(time.time()))
TEST_PROFESSOR = f"test_s3prof_{TIMESTAMP}"
TEST_STUDENT = f"test_s3stu_{TIMESTAMP}"
TEST_PASSWORD = "test123456"
TEST_COURSE_NAME = f"测试课程_{TIMESTAMP}"


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
_professor_id = None
_student_id = None
_student_token = None
_course_id = None
_enrollment_id = None


def _register_and_login_professor():
    global _professor_token, _professor_id
    if _professor_token:
        return _professor_token
    requests.post(f"{BASE_URL}/register", json={
        "username": TEST_PROFESSOR, "password": TEST_PASSWORD, "role": 1, "house_id": None
    })
    resp = requests.post(f"{BASE_URL}/login", json={
        "username": TEST_PROFESSOR, "password": TEST_PASSWORD
    })
    if resp.status_code == 200:
        _professor_token = resp.json()["data"]["token"]
        _professor_id = resp.json()["data"]["user_id"]
    return _professor_token


def _register_student():
    global _student_id, _student_token
    if _student_id:
        return _student_id
    requests.post(f"{BASE_URL}/register", json={
        "username": TEST_STUDENT, "password": TEST_PASSWORD, "role": 0, "house_id": 1
    })
    resp = requests.post(f"{BASE_URL}/login", json={
        "username": TEST_STUDENT, "password": TEST_PASSWORD
    })
    if resp.status_code == 200:
        _student_token = resp.json()["data"]["token"]
        _student_id = resp.json()["data"]["user_id"]
    return _student_id


def _enroll_student_to_course():
    global _enrollment_id, _course_id
    if _enrollment_id:
        return _enrollment_id
    if not _course_id or not _student_id:
        return None
    execute_query(
        "INSERT IGNORE INTO course_enrollment (student_id, course_id, status) VALUES (%s, %s, 1)",
        (_student_id, _course_id),
        commit=True
    )
    result = execute_query(
        "SELECT enrollment_id FROM course_enrollment WHERE student_id = %s AND course_id = %s",
        (_student_id, _course_id),
        fetch_one=True
    )
    if result:
        _enrollment_id = result['enrollment_id']
    return _enrollment_id


def test_create_course():
    global _course_id
    print_test_header("教授创建课程")
    _register_and_login_professor()
    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}
        data = {
            "course_name": TEST_COURSE_NAME,
            "credits": 3,
            "description": "阶段三测试课程-学习魔法基础理论"
        }
        response = requests.post(f"{BASE_URL}/professor/course", json=data, headers=headers)
        print_result(response)
        if response.status_code == 200:
            resp_data = response.json().get("data", {})
            _course_id = resp_data.get("course_id")
            if _course_id and resp_data.get("course_name") == TEST_COURSE_NAME:
                print(f"[OK] 课程创建成功，course_id={_course_id}")
                return True
        print("[FAIL] 课程创建失败")
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_get_courses():
    print_test_header("获取教授课程列表（含选课人数）")
    _register_and_login_professor()
    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}
        response = requests.get(f"{BASE_URL}/professor/courses", headers=headers)
        print_result(response)
        if response.status_code == 200:
            courses = response.json().get("data", [])
            found = any(c.get("course_id") == _course_id for c in courses)
            for c in courses:
                print(f"  - {c['course_name']} (ID: {c['course_id']}, 学分: {c['credits']}, 选课: {c.get('student_count', 0)}人)")
            if found:
                print("[OK] 课程列表包含新创建的课程")
                return True
        print("[FAIL] 课程列表验证失败")
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_update_course():
    print_test_header("教授更新课程信息")
    _register_and_login_professor()
    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}
        data = {
            "course_name": f"{TEST_COURSE_NAME}_更新版",
            "credits": 4,
            "description": "课程描述已更新"
        }
        response = requests.put(f"{BASE_URL}/professor/course/{_course_id}", json=data, headers=headers)
        print_result(response)
        if response.status_code == 200:
            resp_data = response.json().get("data", {})
            if resp_data.get("course_name") == f"{TEST_COURSE_NAME}_更新版" and resp_data.get("credits") == 4:
                print("[OK] 课程更新成功")
                return True
        print("[FAIL] 课程更新失败")
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_add_course_schedule():
    print_test_header("添加课程安排")
    _register_and_login_professor()
    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}
        data = {
            "weekday": 1,
            "start_time": "09:00",
            "end_time": "10:30",
            "classroom": "地下教室"
        }
        response = requests.post(f"{BASE_URL}/professor/course/{_course_id}/schedule", json=data, headers=headers)
        print_result(response)
        if response.status_code == 200:
            resp_data = response.json().get("data", {})
            if resp_data.get("weekday") == 1 and resp_data.get("classroom") == "地下教室":
                print("[OK] 课程安排添加成功")
                return True
        print("[FAIL] 课程安排添加失败")
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_get_course_schedule():
    print_test_header("获取课程安排")
    _register_and_login_professor()
    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}
        response = requests.get(f"{BASE_URL}/professor/course/{_course_id}/schedule", headers=headers)
        print_result(response)
        if response.status_code == 200:
            schedules = response.json().get("data", [])
            print(f"课程安排数: {len(schedules)}")
            for s in schedules:
                print(f"  周{s['weekday']} {s['start_time']}-{s['end_time']} {s.get('classroom', '')}")
            return len(schedules) > 0
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_get_course_students():
    print_test_header("查看选课学生名单")
    _register_and_login_professor()
    _register_student()
    _enroll_student_to_course()
    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}
        response = requests.get(f"{BASE_URL}/professor/course/{_course_id}/students", headers=headers)
        print_result(response)
        if response.status_code == 200:
            students = response.json().get("data", [])
            print(f"选课学生数: {len(students)}")
            found = any(s.get("student_id") == _student_id for s in students)
            for s in students:
                print(f"  - {s['student_name']} (学院: {s.get('house_name', 'N/A')})")
            if found:
                print("[OK] 学生名单包含测试学生")
                return True
        print("[FAIL] 学生名单验证失败")
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_record_class_performance():
    print_test_header("记录课堂表现（关联积分系统）")
    _register_and_login_professor()
    _register_student()
    _enroll_student_to_course()

    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}

        before_house = execute_query(
            "SELECT total_points FROM house WHERE house_id = 1",
            fetch_one=True
        )
        before_points = before_house['total_points'] if before_house else 0
        print(f"学院加分前总分: {before_points}")

        data = {
            "student_id": _student_id,
            "course_id": _course_id,
            "performance_type": 1,
            "score": 10,
            "reason": "魔药学课堂回答正确"
        }
        response = requests.post(f"{BASE_URL}/professor/class-performance", json=data, headers=headers)
        print_result(response)

        if response.status_code != 200:
            print("[FAIL] 课堂表现记录失败")
            return False

        resp_data = response.json().get("data", {})
        performance_id = resp_data.get("performance_id")
        point_log_id = resp_data.get("point_log_id")
        print(f"performance_id={performance_id}, point_log_id={point_log_id}")

        if not performance_id or not point_log_id:
            print("[FAIL] 未返回 performance_id 或 point_log_id")
            return False

        time.sleep(0.5)

        after_house = execute_query(
            "SELECT total_points FROM house WHERE house_id = 1",
            fetch_one=True
        )
        after_points = after_house['total_points'] if after_house else 0
        print(f"学院加分后总分: {after_points}")

        if after_points == before_points + 10:
            print("[OK] 课堂表现记录成功，积分联动正常，触发器自动更新学院总分")
            return True
        else:
            print(f"[FAIL] 触发器联动异常：预期 {before_points + 10}，实际 {after_points}")
            return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_get_course_performances():
    print_test_header("查看课堂表现记录")
    _register_and_login_professor()
    _register_student()
    _enroll_student_to_course()

    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}

        requests.post(f"{BASE_URL}/professor/class-performance", json={
            "student_id": _student_id,
            "course_id": _course_id,
            "performance_type": 2,
            "score": 5,
            "reason": "课堂作业完成良好"
        }, headers=headers)

        response = requests.get(f"{BASE_URL}/professor/course/{_course_id}/performances", headers=headers)
        print_result(response)

        if response.status_code == 200:
            data = response.json().get("data", {})
            performances = data.get("performances", [])
            total = data.get("total", 0)
            print(f"\n课堂表现记录总数: {total}")
            for p in performances:
                type_map = {1: "回答问题", 2: "课堂作业", 3: "小组合作"}
                print(f"  - {p['student_name']}: {type_map.get(p['performance_type'], 'N/A')} {p['score']:+d}分 ({p['reason']})")
            if total > 0 and len(performances) > 0:
                print("[OK] 课堂表现记录查询正常")
                return True
        print("[FAIL] 课堂表现记录查询失败")
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_delete_schedule():
    print_test_header("删除课程安排")
    _register_and_login_professor()
    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}

        add_resp = requests.post(f"{BASE_URL}/professor/course/{_course_id}/schedule", json={
            "weekday": 3, "start_time": "14:00", "end_time": "15:30", "classroom": "天文塔"
        }, headers=headers)
        schedule_id = add_resp.json().get("data", {}).get("schedule_id")
        print(f"添加测试安排 schedule_id={schedule_id}")

        response = requests.delete(f"{BASE_URL}/professor/schedule/{schedule_id}", headers=headers)
        print_result(response)

        if response.status_code == 200:
            print("[OK] 课程安排删除成功")
            return True
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_delete_course():
    print_test_header("删除课程（级联删除关联数据）")
    _register_and_login_professor()
    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}

        create_resp = requests.post(f"{BASE_URL}/professor/course", json={
            "course_name": f"待删除课程_{TIMESTAMP}",
            "credits": 2,
            "description": "将被删除的测试课程"
        }, headers=headers)
        temp_course_id = create_resp.json().get("data", {}).get("course_id")
        print(f"创建临时课程 course_id={temp_course_id}")

        requests.post(f"{BASE_URL}/professor/course/{temp_course_id}/schedule", json={
            "weekday": 5, "start_time": "10:00", "end_time": "11:00", "classroom": "教室A"
        }, headers=headers)

        response = requests.delete(f"{BASE_URL}/professor/course/{temp_course_id}", headers=headers)
        print_result(response)

        if response.status_code == 200:
            remaining = execute_query(
                "SELECT COUNT(*) AS cnt FROM course WHERE course_id = %s",
                (temp_course_id,), fetch_one=True
            )
            if remaining['cnt'] == 0:
                print("[OK] 课程及关联数据已级联删除")
                return True
        print("[FAIL] 课程删除失败")
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_unauthorized_access_course():
    print_test_header("权限验证：非课程所属教授操作（应该失败）")
    _register_and_login_professor()
    try:
        professor2_name = f"test_other_prof_{TIMESTAMP}"
        requests.post(f"{BASE_URL}/register", json={
            "username": professor2_name, "password": TEST_PASSWORD, "role": 1, "house_id": None
        })
        login2 = requests.post(f"{BASE_URL}/login", json={
            "username": professor2_name, "password": TEST_PASSWORD
        })
        token2 = login2.json()["data"]["token"]

        headers = {"Authorization": f"Bearer {token2}"}
        response = requests.put(f"{BASE_URL}/professor/course/{_course_id}", json={
            "course_name": "篡改课程名"
        }, headers=headers)
        print_result(response)
        if response.status_code == 403:
            print("[OK] 系统正确拦截了非所属教授的修改请求")
            return True
        print("[FAIL] 系统未能拦截非所属教授的操作")
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_student_unauthorized_professor_api():
    print_test_header("权限验证：学生Token访问教授课程接口（应该失败）")
    _register_student()
    try:
        headers = {"Authorization": f"Bearer {_student_token}"}
        response = requests.post(f"{BASE_URL}/professor/course", json={
            "course_name": "学生无法创建课程",
            "credits": 1,
            "description": "应该被拦截"
        }, headers=headers)
        print_result(response)
        if response.status_code == 403:
            print("[OK] 系统正确拦截了学生访问教授接口")
            return True
        print("[FAIL] 系统未能拦截学生越权访问")
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def run_stage3_professor_course_tests():
    print("\n" + "=" * 60)
    print("霍格沃茨 MIS - 阶段三测试套件 [教授端课程系统]（组员3 余雨航）")
    print("=" * 60)

    results = []

    results.append(("创建课程", test_create_course()))
    results.append(("获取课程列表（含选课人数）", test_get_courses()))
    results.append(("更新课程信息", test_update_course()))
    results.append(("添加课程安排", test_add_course_schedule()))
    results.append(("获取课程安排", test_get_course_schedule()))
    results.append(("查看选课学生名单", test_get_course_students()))
    results.append(("课堂表现记录+积分联动", test_record_class_performance()))
    results.append(("查看课堂表现记录", test_get_course_performances()))
    results.append(("删除课程安排", test_delete_schedule()))
    results.append(("删除课程（级联）", test_delete_course()))
    results.append(("权限验证-非所属教授", test_unauthorized_access_course()))
    results.append(("权限验证-学生越权", test_student_unauthorized_professor_api()))

    print("\n" + "=" * 60)
    print("阶段三[教授端课程系统]测试结果汇总")
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
        print("恭喜！阶段三[教授端课程系统]所有测试通过！\n")
    else:
        print("[WARN] 部分测试失败，请检查代码。\n")

    return passed, failed


if __name__ == "__main__":
    print("[WARN] 请先启动 Flask 应用，然后运行此测试脚本。")
    print("启动命令: python py/app.py\n")
