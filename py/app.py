import os
import pymysql
from flask import Flask,request,jsonify
from dotenv import load_dotenv

#加载环境变量
load_dotenv()

app=Flask(__name__)

#获取数据库配置
DB_HOST=os.getenv("DB_HOST")
DB_PORT=int(os.getenv("DB_PORT",3306))
DB_USER=os.getenv("DB_USER")
DB_PASSWORD=os.getenv("DB_PASSWORD")
#假设你在MySQL中创建的数据库名为mis
DB_NAME="mis"

#测试数据库连接
@app.route('/api/test_db',methods=['GET'])
def test_db():
    try:
        conn=pymysql.connect(host=DB_HOST,port=DB_PORT,user=DB_USER,password=DB_PASSWORD,database=DB_NAME)
        cursor=conn.cursor()
        cursor.execute("SELECT VERSION();")
        db_version=cursor.fetchone()
        conn.close()
        return jsonify({"code":200,"msg":"数据库连接成功!","data":db_version})
    except Exception as e:
        return jsonify({"code":500,"msg":str(e),"data":None})

if __name__=='__main__':
    app.run(debug=True,port=5000)