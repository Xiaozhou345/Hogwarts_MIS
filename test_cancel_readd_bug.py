"""
测试时间转换器：取消后重新添加的bug修复
问题：选择活动 → 取消 → 再次添加 → 报错 duplicate entity
修复：检查已存在的记录并重新激活，而不是插入新记录
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def login(username, password):
    """登录获取token"""
    response = requests.post(f"{BASE_URL}/api/login", json={
        "username": username,
        "password": password
    })
    if response.status_code == 200:
        data = response.json()
        if data["code"] == 200:
            return data["data"]["token"]
    return None

def test_cancel_and_readd():
    """测试：选择活动 → 取消 → 再次添加"""
    print("=" * 70)
    print("🧪 测试：时间转换器 - 取消后重新添加功能")
    print("=" * 70)

    # 1. 登录（使用第一名学院的学生）
    print("\n【步骤1】登录第一名学院学生账号")
    username = "demo_harry"
    password = "123456"

    token = login(username, password)
    if not token:
        print("❌ 登录失败")
        return False

    print(f"✅ 登录成功：{username}")
    headers = {"Authorization": f"Bearer {token}"}

    # 2. 检查时间转换器状态
    print("\n【步骤2】检查时间转换器状态")
    response = requests.get(f"{BASE_URL}/api/student/time-turner/status", headers=headers)
    data = response.json()

    if data["code"] != 200 or not data["data"]["has_time_turner"]:
        print(f"❌ 该学生没有时间转换器权限，学院：{data['data'].get('house_name')}")
        print("   提示：需要确保该学生所属学院是第一名")
        return False

    print(f"✅ 拥有时间转换器，学院：{data['data']['house_name']}")

    # 3. 第一次选择活动
    print("\n【步骤3】第一次选择活动")
    activity_data = {
        "activity_id": 1,  # 去海格小屋喝茶
        "weekday": 1,      # 周一
        "start_time": "09:00:00",
        "end_time": "10:30:00"
    }

    response = requests.post(
        f"{BASE_URL}/api/student/activity/enroll",
        headers=headers,
        json=activity_data
    )
    data = response.json()

    if data["code"] != 200:
        print(f"❌ 第一次选择失败：{data['msg']}")
        print(f"   提示：确保周一09:00-10:30有课程安排")
        return False

    enrollment_id = data["data"]["enrollment_id"]
    print(f"✅ 第一次选择成功，enrollment_id: {enrollment_id}")
    print(f"   消息：{data['msg']}")

    # 4. 取消活动
    print("\n【步骤4】取消活动")
    response = requests.delete(
        f"{BASE_URL}/api/student/activity/enroll/{enrollment_id}",
        headers=headers
    )
    data = response.json()

    if data["code"] != 200:
        print(f"❌ 取消失败：{data['msg']}")
        return False

    print(f"✅ 取消成功")
    print(f"   消息：{data['msg']}")

    # 5. 再次选择相同的活动（这是关键测试点）
    print("\n【步骤5】再次选择相同时间段的活动（关键测试）")
    response = requests.post(
        f"{BASE_URL}/api/student/activity/enroll",
        headers=headers,
        json=activity_data
    )
    data = response.json()

    if data["code"] != 200:
        print(f"❌ 第二次选择失败：{data['msg']}")
        print(f"   错误代码：{data['code']}")
        print(f"   完整响应：{json.dumps(data, indent=2, ensure_ascii=False)}")
        return False

    new_enrollment_id = data["data"]["enrollment_id"]
    print(f"✅ 第二次选择成功，enrollment_id: {new_enrollment_id}")
    print(f"   消息：{data['msg']}")

    # 6. 验证活动列表
    print("\n【步骤6】验证活动列表")
    response = requests.get(f"{BASE_URL}/api/student/my-activities", headers=headers)
    data = response.json()

    if data["code"] == 200:
        activities = data["data"]
        print(f"✅ 当前活动数量：{len(activities)}")
        for act in activities:
            print(f"   - {act['activity_name_cn']} (enrollment_id: {act['enrollment_id']})")

    # 7. 清理：再次取消活动
    print("\n【步骤7】清理：取消活动")
    response = requests.delete(
        f"{BASE_URL}/api/student/activity/enroll/{new_enrollment_id}",
        headers=headers
    )
    data = response.json()

    if data["code"] == 200:
        print(f"✅ 清理成功")

    print("\n" + "=" * 70)
    print("🎉 测试通过！bug已修复！")
    print("=" * 70)
    return True

def test_cancel_and_readd_different_activity():
    """测试：取消活动后，在同一时间段选择不同的活动"""
    print("\n\n" + "=" * 70)
    print("🧪 测试：取消后在同一时间段选择不同活动")
    print("=" * 70)

    # 1. 登录
    print("\n【步骤1】登录")
    token = login("demo_harry", "123456")
    if not token:
        print("❌ 登录失败")
        return False

    print(f"✅ 登录成功")
    headers = {"Authorization": f"Bearer {token}"}

    # 2. 选择活动1
    print("\n【步骤2】选择活动1（去海格小屋喝茶）")
    activity1_data = {
        "activity_id": 1,
        "weekday": 2,  # 周二
        "start_time": "14:00:00",
        "end_time": "15:30:00"
    }

    response = requests.post(
        f"{BASE_URL}/api/student/activity/enroll",
        headers=headers,
        json=activity1_data
    )
    data = response.json()

    if data["code"] != 200:
        print(f"❌ 选择活动1失败：{data['msg']}")
        return False

    enrollment_id1 = data["data"]["enrollment_id"]
    print(f"✅ 选择活动1成功，enrollment_id: {enrollment_id1}")

    # 3. 取消活动1
    print("\n【步骤3】取消活动1")
    response = requests.delete(
        f"{BASE_URL}/api/student/activity/enroll/{enrollment_id1}",
        headers=headers
    )
    data = response.json()

    if data["code"] != 200:
        print(f"❌ 取消失败：{data['msg']}")
        return False

    print(f"✅ 取消成功")

    # 4. 在同一时间段选择活动2（不同的活动）
    print("\n【步骤4】在同一时间段选择活动2（去霍格莫德村游玩）")
    activity2_data = {
        "activity_id": 2,  # 不同的活动
        "weekday": 2,      # 相同时间
        "start_time": "14:00:00",
        "end_time": "15:30:00"
    }

    response = requests.post(
        f"{BASE_URL}/api/student/activity/enroll",
        headers=headers,
        json=activity2_data
    )
    data = response.json()

    if data["code"] != 200:
        print(f"❌ 选择活动2失败：{data['msg']}")
        return False

    enrollment_id2 = data["data"]["enrollment_id"]
    print(f"✅ 选择活动2成功，enrollment_id: {enrollment_id2}")
    print(f"   消息：{data['msg']}")

    # 5. 清理
    print("\n【步骤5】清理")
    requests.delete(f"{BASE_URL}/api/student/activity/enroll/{enrollment_id2}", headers=headers)
    print(f"✅ 清理成功")

    print("\n" + "=" * 70)
    print("🎉 测试通过！")
    print("=" * 70)
    return True

if __name__ == "__main__":
    print("\n")
    print("█" * 70)
    print("  时间转换器 Bug 修复验证测试")
    print("█" * 70)

    try:
        # 测试1：取消后重新添加相同活动
        test1_passed = test_cancel_and_readd()

        # 测试2：取消后添加不同活动
        test2_passed = test_cancel_and_readd_different_activity()

        print("\n\n" + "█" * 70)
        print("  测试总结")
        print("█" * 70)
        print(f"测试1（取消后重新添加相同活动）: {'✅ 通过' if test1_passed else '❌ 失败'}")
        print(f"测试2（取消后添加不同活动）: {'✅ 通过' if test2_passed else '❌ 失败'}")

        if test1_passed and test2_passed:
            print("\n🎉🎉🎉 所有测试通过！Bug已成功修复！🎉🎉🎉")
        else:
            print("\n⚠️  有测试失败，请检查")

    except Exception as e:
        print(f"\n❌ 测试过程中发生异常：{str(e)}")
        import traceback
        traceback.print_exc()
