import pymysql
from config import Config

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

def execute_query(sql, params=None, fetch_one=False, fetch_all=False, commit=False, return_lastrowid=False):
    """
    执行数据库查询的通用函数
    :param sql: SQL 语句
    :param params: 参数元组
    :param fetch_one: 是否返回单条记录
    :param fetch_all: 是否返回所有记录
    :param commit: 是否需要提交（INSERT/UPDATE/DELETE）
    :param return_lastrowid: 是否返回最后插入的自增ID
    :return: 查询结果、影响的行数或自增ID
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(sql, params)

        if commit:
            conn.commit()
            if return_lastrowid:
                return cursor.lastrowid
            return cursor.rowcount

        if fetch_one:
            return cursor.fetchone()

        if fetch_all:
            return cursor.fetchall()

        return None

    except Exception as e:
        if commit:
            conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()
