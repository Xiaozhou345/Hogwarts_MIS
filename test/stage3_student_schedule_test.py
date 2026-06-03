import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'py'))
import requests
import json
import time
from db_utils import execute_query

BASE_URL = "http://127.0.0.1:5000/api"

TIMESTAMP = str(int(time.time()))
TEST_STUDENT = f"test_schedstu_{TIMESTAMP}"
TEST_PROFESSOR = f"test_schedprof_{TIMESTAMP}"
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


_student_token = None
_student_id = None
_professor_token = None
_course_id_1 = None
_course_id_2 = None


def _register_and_login():
    global _student_token, _student_id, _professor_token
    if _student_token and _professor_token:
        return

    resp = requests.post(f"{BASE_URL}/register", json={
        "username": TEST_STUDENT, "password": TEST_PASSWORD, "role": 0, "house_id": 1
    })
    login = requests.post(f"{BASE_URL}/login", json={
        "username": TEST_STUDENT, "password": TEST_PASSWORD
    })
    if login.status_code == 200:
        _student_token = login.json()["data"]["token"]
        _student_id = login.json()["data"]["user_id"]

    resp = requests.post(f"{BASE_URL}/register", json={
        "username": TEST_PROFESSOR, "password": TEST_PASSWORD, "role": 1, "house_id": None
    })
    login2 = requests.post(f"{BASE_URL}/login", json={
        "username": TEST_PROFESSOR, "password": TEST_PASSWORD
    })
    if login2.status_code == 200:
        _professor_token = login2.json()["data"]["token"]


def _create_course_and_enroll():
    global _course_id_1, _course_id_2
    if _course_id_1 and _course_id_2:
        return

    headers = {"Authorization": f"Bearer {_professor_token}"}

    course1 = requests.post(f"{BASE_URL}/professor/course", json={
        "course_name": f"课程A_{TIMESTAMP}",
        "credits": 3,
        "description": "测试课程A"
    }, headers=headers)
    _course_id_1 = course1.json()["data"]["course_id"]

    course2 = requests.post(f"{BASE_URL}/professor/course", json={
        "course_name": f"课程B_{TIMESTAMP}",
        "credits": 2,
        "description": "测试课程B"
    }, headers=headers)
    _course_id_2 = course2.json()["data"]["course_id"]

    requests.post(f"{BASE_URL}/professor/course/{_course_id_1}/schedule", json={
        "weekday": 1, "start_time": "09:00", "end_time": "10:30", "classroom": "教室301"
    }, headers=headers)
    requests.post(f"{BASE_URL}/professor/course/{_course_id_1}/schedule", json={
        "weekday": 3, "start_time": "14:00", "end_time": "15:30", "classroom": "实验室A"
    }, headers=headers)
    requests.post(f"{BASE_URL}/professor/course/{_course_id_2}/schedule", json={
        "weekday": 2, "start_time": "10:00", "end_time": "12:00", "classroom": "教室202"
    }, headers=headers)

    execute_query(
        "INSERT IGNORE INTO course_enrollment (student_id, course_id, status) VALUES (%s, %s, 1)",
        (_student_id, _course_id_1), commit=True
    )
    execute_query(
        "INSERT IGNORE INTO course_enrollment (student_id, course_id, status) VALUES (%s, %s, 1)",
        (_student_id, _course_id_2), commit=True
    )


def test_schedule_empty():
    print_test_header("学生未选课时课程表为空")
    try:
        temp_student = f"empty_sched_{TIMESTAMP}"
        requests.post(f"{BASE_URL}/register", json={
            "username": temp_student, "password": TEST_PASSWORD, "role": 0, "house_id": 1
        })
        login = requests.post(f"{BASE_URL}/login", json={
            "username": temp_student, "password": TEST_PASSWORD
        })
        token = login.json()["data"]["token"]

        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/student/schedule", headers=headers)
        print_result(response)

        if response.status_code == 200:
            data = response.json()["data"]
            total_courses = sum(len(v) for v in data.values())
            if total_courses == 0:
                print("[OK] 未选课学生的课程表全部为空")
                return True
            else:
                print(f"[FAIL] 课程表不为空，有 {total_courses} 条记录")
                return False
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_schedule_with_courses():
    print_test_header("学生选课后课程表正确返回")
    _register_and_login()
    _create_course_and_enroll()

    try:
        headers = {"Authorization": f"Bearer {_student_token}"}
        response = requests.get(f"{BASE_URL}/student/schedule", headers=headers)
        print_result(response)

        if response.status_code == 200:
            data = response.json()["data"]
            monday = data.get("Monday", [])
            tuesday = data.get("Tuesday", [])
            wednesday = data.get("Wednesday", [])

            print(f"\n周一课程: {len(monday)} 节")
            for c in monday:
                print(f"  - {c['course_name']}: {c['start_time']}-{c['end_time']} ({c['classroom']})")
            print(f"周二课程: {len(tuesday)} 节")
            for c in tuesday:
                print(f"  - {c['course_name']}: {c['start_time']}-{c['end_time']} ({c['classroom']})")
            print(f"周三课程: {len(wednesday)} 节")
            for c in wednesday:
                print(f"  - {c['course_name']}: {c['start_time']}-{c['end_time']} ({c['classroom']})")

            if len(monday) > 0 and len(tuesday) > 0:
                print("[OK] 课程表正确返回了周一和周二课程")
                return True
            else:
                print("[FAIL] 课程表缺少预期课程")
                return False
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_schedule_time_format():
    print_test_header("课程表时间格式验证（HH:MM:SS）")
    _register_and_login()
    _create_course_and_enroll()

    try:
        headers = {"Authorization": f"Bearer {_student_token}"}
        response = requests.get(f"{BASE_URL}/student/schedule", headers=headers)

        if response.status_code == 200:
            data = response.json()["data"]
            all_courses = []
            for day_courses in data.values():
                all_courses.extend(day_courses)

            if len(all_courses) == 0:
                print("[FAIL] 课程表无数据")
                return False

            all_valid = True
            for c in all_courses:
                start = c['start_time']
                end = c['end_time']
                time_parts_s = start.split(':')
                time_parts_e = end.split(':')

                if len(time_parts_s) >= 2 and len(time_parts_e) >= 2:
                    print(f"  {c['course_name']}: {start} - {end}")
                else:
                    print(f"  [ERROR] {c['course_name']}: 时间格式异常 start={start} end={end}")
                    all_valid = False

            if all_valid:
                print("[OK] 所有课程时间格式正确")
                return True
            else:
                print("[FAIL] 部分课程时间格式不正确")
                return False
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_schedule_weekday_grouping():
    print_test_header("课程表按周分组验证")
    _register_and_login()
    _create_course_and_enroll()

    try:
        headers = {"Authorization": f"Bearer {_student_token}"}
        response = requests.get(f"{BASE_URL}/student/schedule", headers=headers)

        if response.status_code == 200:
            data = response.json()["data"]
            expected_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            has_all_days = all(day in data for day in expected_days)

            if has_all_days:
                print(f"[OK] 返回了全部7天: {', '.join(expected_days)}")
            else:
                missing = [d for d in expected_days if d not in data]
                print(f"[FAIL] 缺少: {missing}")
                return False

            monday = data.get("Monday", [])
            has_course_a = any(f"课程A_{TIMESTAMP}" in c.get("course_name", "") for c in monday)
            if not has_course_a:
                print(f"[FAIL] 周一课程A未正确分组")
                return False

            print(f"[OK] 课程A出现在周一({len(monday)}节)，分组正确")
            return True
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_schedule_multiple_same_day():
    print_test_header("同一天多门课程正确显示")
    _register_and_login()
    _create_course_and_enroll()

    try:
        headers = {"Authorization": f"Bearer {_professor_token}"}

        course_c = requests.post(f"{BASE_URL}/professor/course", json={
            "course_name": f"课程C_{TIMESTAMP}",
            "credits": 1,
            "description": "测试课程C"
        }, headers=headers)
        course_c_id = course_c.json()["data"]["course_id"]

        requests.post(f"{BASE_URL}/professor/course/{course_c_id}/schedule", json={
            "weekday": 1, "start_time": "11:00", "end_time": "12:00", "classroom": "教室505"
        }, headers=headers)

        execute_query(
            "INSERT IGNORE INTO course_enrollment (student_id, course_id, status) VALUES (%s, %s, 1)",
            (_student_id, course_c_id), commit=True
        )

        student_headers = {"Authorization": f"Bearer {_student_token}"}
        response = requests.get(f"{BASE_URL}/student/schedule", headers=student_headers)
        print_result(response)

        if response.status_code == 200:
            data = response.json()["data"]
            monday = data.get("Monday", [])
            print(f"\n周一课程数: {len(monday)} 节")
            for c in monday:
                print(f"  - {c['course_name']}: {c['start_time']}-{c['end_time']}")

            course_a_found = any(f"课程A_{TIMESTAMP}" in c.get("course_name", "") for c in monday)
            course_c_found = any(f"课程C_{TIMESTAMP}" in c.get("course_name", "") for c in monday)

            if course_a_found and course_c_found:
                print("[OK] 周一同时显示了课程A和课程C")
                return True
            else:
                print(f"[FAIL] 课程A={course_a_found}, 课程C={course_c_found}")
                return False
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def test_schedule_course_info_integrity():
    print_test_header("课程表课程信息完整性验证")
    _register_and_login()
    _create_course_and_enroll()

    try:
        headers = {"Authorization": f"Bearer {_student_token}"}
        response = requests.get(f"{BASE_URL}/student/schedule", headers=headers)

        if response.status_code == 200:
            data = response.json()["data"]
            all_courses = []
            for day_courses in data.values():
                all_courses.extend(day_courses)

            if len(all_courses) == 0:
                print("[FAIL] 课程表无数据")
                return False

            required_fields = ["course_name", "start_time", "end_time", "classroom", "professor_name"]
            all_ok = True
            for c in all_courses:
                missing_fields = [f for f in required_fields if f not in c or not c[f]]
                if missing_fields:
                    print(f"  [ERROR] {c.get('course_name', 'N/A')} 缺少字段: {missing_fields}")
                    all_ok = False
                else:
                    print(f"  {c['course_name']} - 教授:{c['professor_name']} 教室:{c['classroom']} {c['start_time']}-{c['end_time']}")

            if all_ok:
                print(f"[OK] 所有 {len(all_courses)} 条课程信息完整")
                return True
            else:
                return False
        return False
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)}")
        return False


def run_stage3_student_schedule_tests():
    print("\n" + "=" * 60)
    print("霍格沃茨 MIS - 阶段三补充测试套件 [学生课程表]（组员3 余雨航）")
    print("=" * 60)

    results = []

    results.append(("空课程表验证", test_schedule_empty()))
    results.append(("选课后课程表显示", test_schedule_with_courses()))
    results.append(("时间格式验证", test_schedule_time_format()))
    results.append(("按周分组验证", test_schedule_weekday_grouping()))
    results.append(("同天多课程显示", test_schedule_multiple_same_day()))
    results.append(("课程信息完整性", test_schedule_course_info_integrity()))

    print("\n" + "=" * 60)
    print("阶段三补充[学生课程表]测试结果汇总")
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
        print("恭喜！阶段三补充[学生课程表]所有测试通过！\n")
    else:
        print("[WARN] 部分测试失败，请检查代码。\n")

    return passed, failed


if __name__ == "__main__":
    print("[WARN] 请先启动 Flask 应用，然后运行此测试脚本。")
    print("启动命令: python py/app.py\n")
