import jwt
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from config import Config

def hash_password(password):
    """使用 SHA256 哈希加密密码"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """验证密码"""
    return hash_password(password) == password_hash

def generate_token(user_id, role):
    """生成 JWT Token"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS)
    }
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    return token

def decode_token(token):
    """解码 JWT Token"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """装饰器：验证 Token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"code": 401, "msg": "缺少认证令牌", "data": None}), 401

        if token.startswith('Bearer '):
            token = token[7:]

        payload = decode_token(token)

        if not payload:
            return jsonify({"code": 401, "msg": "令牌无效或已过期", "data": None}), 401

        request.user_id = payload['user_id']
        request.role = payload['role']

        return f(*args, **kwargs)

    return decorated

def role_required(required_role):
    """装饰器：验证用户角色"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.role != required_role:
                return jsonify({"code": 403, "msg": "权限不足", "data": None}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
