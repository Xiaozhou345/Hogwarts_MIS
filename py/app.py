import sys
import os
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from db_utils import execute_query
from auth_utils import hash_password, verify_password, generate_token, token_required
from professor_api import professor_bp
from student_api import student_bp
from public_api import public_bp

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')
app.register_blueprint(professor_bp)
app.register_blueprint(student_bp)
app.register_blueprint(public_bp)

@app.route('/api/test_db', methods=['GET'])
def test_db():
    """测试数据库连接"""
    try:
        result = execute_query("SELECT VERSION();", fetch_one=True)
        return jsonify({"code": 200, "msg": "数据库连接成功!", "data": result})
    except Exception as e:
        return jsonify({"code": 500, "msg": str(e), "data": None})

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')
        house_id = data.get('house_id')

        if not username or not password or role is None:
            return jsonify({"code": 400, "msg": "缺少必要参数", "data": None}), 400

        if role == 0 and not house_id:
            return jsonify({"code": 400, "msg": "学生必须选择学院", "data": None}), 400

        if role == 1:
            house_id = None

        existing_user = execute_query(
            "SELECT user_id FROM sys_user WHERE username = %s",
            (username,),
            fetch_one=True
        )

        if existing_user:
            return jsonify({"code": 400, "msg": "用户名已存在", "data": None}), 400

        password_hash = hash_password(password)

        execute_query(
            "INSERT INTO sys_user (username, password_hash, role, house_id) VALUES (%s, %s, %s, %s)",
            (username, password_hash, role, house_id),
            commit=True
        )

        return jsonify({"code": 200, "msg": "注册成功", "data": None})

    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"code": 400, "msg": "缺少用户名或密码", "data": None}), 400

        user = execute_query(
            "SELECT user_id, password_hash, role, house_id FROM sys_user WHERE username = %s",
            (username,),
            fetch_one=True
        )

        if not user:
            return jsonify({"code": 400, "msg": "用户名或密码错误", "data": None}), 400

        if not verify_password(password, user['password_hash']):
            return jsonify({"code": 400, "msg": "用户名或密码错误", "data": None}), 400

        token = generate_token(user['user_id'], user['role'])

        return jsonify({
            "code": 200,
            "msg": "登录成功",
            "data": {
                "token": token,
                "role": user['role'],
                "user_id": user['user_id'],
                "house_id": user['house_id']
            }
        })

    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}), 500

@app.route('/api/logout', methods=['POST'])
@token_required
def logout():
    """用户登出"""
    return jsonify({"code": 200, "msg": "已安全退出", "data": None})

if __name__ == '__main__':
    # 测试模块，从测试调度代码文件调用测试，在env中配置开关
    if Config.TEST_MODE:
        print("\n" + "="*50)
        print("[TEST] 测试模式已启动")
        print("="*50 + "\n")
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        import threading
        def run_flask():
            app.run(debug=False, port=Config.PORT, use_reloader=False)

        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()

        import time
        time.sleep(2)

        from test.test_runner import run_by_env
        run_by_env()
    # 非测试模式，启动Flask应用，根据配置文件中的DEBUG开关设置调试模式和端口号
    else:
        print("\n" + "="*50)
        print("霍格沃茨 MIS 系统启动")
        print(f"运行地址: http://127.0.0.1:{Config.PORT}")
        print(f"调试模式: {'开启' if Config.DEBUG else '关闭'}")
        print("="*50 + "\n")
        app.run(debug=Config.DEBUG, port=Config.PORT)
