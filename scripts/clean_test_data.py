#!/usr/bin/env python3
"""清理测试数据脚本"""
import pymysql

def clean_test_data():
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql2026',
        database='mis'
    )
    cursor = conn.cursor()

    try:
        # 删除测试用户（用户名包含 test_ 的）
        cursor.execute("DELETE FROM sys_user WHERE username LIKE 'test_%'")
        deleted_users = cursor.rowcount

        # 重置学院总分（可选）
        cursor.execute("UPDATE house SET total_points = 0")

        conn.commit()

        print(f"✅ 已删除 {deleted_users} 个测试用户")
        print(f"✅ 已重置学院总分")

        # 显示剩余用户
        cursor.execute("SELECT username, role FROM sys_user")
        remaining = cursor.fetchall()
        print(f"\n📊 剩余用户 ({len(remaining)} 个):")
        for user in remaining:
            role_name = "学生" if user[1] == 0 else "教授"
            print(f"  - {user[0]} ({role_name})")

    except Exception as e:
        conn.rollback()
        print(f"❌ 错误: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("⚠️  即将清理所有测试数据...")
    confirm = input("确认清理？(yes/no): ")
    if confirm.lower() == 'yes':
        clean_test_data()
    else:
        print("已取消")
