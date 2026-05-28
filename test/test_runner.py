import sys
import os

from .stage1_test import run_stage1_tests
from .stage1_professor_test import run_stage1_professor_tests
from .stage1_student_public_test import run_stage1_student_public_tests
from .stage2_professor_test import run_stage2_professor_tests

TEST_SUITES = {
    "auth": {
        "name": "stage1_auth",
        "label": "阶段一[鉴权]：注册登录测试（组员2 Noa）",
        "func": run_stage1_tests,
        "module": "stage1_test"
    },
    "professor": {
        "name": "stage1_professor",
        "label": "阶段一[教授端]：业务写入测试（组员3 余雨航）",
        "func": run_stage1_professor_tests,
        "module": "stage1_professor_test"
    },
    "student": {
        "name": "stage1_student_public",
        "label": "阶段一[学生端+公共]：业务读取测试（组员4 费翔鸿）",
        "func": run_stage1_student_public_tests,
        "module": "stage1_student_public_test"
    },
    "professor2": {
        "name": "stage2_professor",
        "label": "阶段二[教授端]：API完善与边界校验（组员3 余雨航）",
        "func": run_stage2_professor_tests,
        "module": "stage2_professor_test"
    }
}


def show_menu():
    print("\n" + "=" * 50)
    print("霍格沃茨 MIS - 测试调度器")
    print("=" * 50)
    print("\n可选测试套件：")
    for key, suite in TEST_SUITES.items():
        print(f"  [{key}] {suite['label']}")
    print(f"  [all] 运行全部测试")
    print(f"  [q] 退出")
    print("-" * 50)


def run_selected(selections):
    if not selections:
        print("[WARN] 未选择任何测试套件")
        return

    selected_suites = []
    for sel in selections:
        sel = sel.strip()
        if sel in ("0", "all"):
            selected_suites = list(TEST_SUITES.values())
            break
        if sel.lower() == "q":
            print("已退出")
            return
        if sel in TEST_SUITES:
            selected_suites.append(TEST_SUITES[sel])
        else:
            print(f"[WARN] 忽略无效选项: {sel}")

    if not selected_suites:
        print("[WARN] 没有有效的测试套件被选中")
        return

    total_passed = 0
    total_failed = 0

    for suite in selected_suites:
        print(f"\n正在加载测试套件: {suite['label']} ...")
        try:
            passed, failed = suite["func"]()
            total_passed += passed
            total_failed += failed
        except Exception as e:
            print(f"[FAIL] 测试套件 [{suite['name']}] 运行异常: {str(e)}")
            total_failed += 1

    print("\n" + "=" * 60)
    print("全部测试汇总")
    print("=" * 60)
    total = total_passed + total_failed
    print(f"总计: {total} 个测试")
    print(f"[PASS]: {total_passed}")
    print(f"[FAIL]: {total_failed}")
    if total > 0:
        print(f"通过率: {total_passed / total * 100:.1f}%")
    print("=" * 60 + "\n")


def run_all():
    run_selected(["all"])


def run_single(suite_key):
    if suite_key in TEST_SUITES:
        run_selected([suite_key])
    else:
        print(f"[FAIL] 未知的测试套件: {suite_key}")
        print(f"可用套件: {list(TEST_SUITES.keys())}")


def run_interactive():
    show_menu()
    choice = input("请输入要运行的测试套件标识（多个用逗号分隔，如 auth,professor）: ").strip()
    if not choice:
        print("已退出")
        return
    selections = [c.strip() for c in choice.split(",")]
    run_selected(selections)


def run_by_env():
    env_selection = os.getenv("TEST_SUITE", "all")
    selections = [c.strip() for c in env_selection.split(",")]
    run_selected(selections)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--all":
            run_all()
        elif arg == "--menu":
            run_interactive()
        else:
            selections = arg.split(",")
            run_selected(selections)
    else:
        run_interactive()
