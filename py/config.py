import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

class Config:
    # 数据库配置
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "mis")

    # JWT 配置
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "hogwarts_secret_key_2026")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24

    # 测试模式开关
    TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

    # Flask 配置
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    PORT = int(os.getenv("PORT", 5000))
