import pymysql

conn = pymysql.connect(
    host='192.168.31.108',
    port=3307,
    user='root',
    password='0609',
    cursorclass=pymysql.cursors.DictCursor
)
cursor = conn.cursor()
cursor.execute("SHOW DATABASES")
for row in cursor.fetchall():
    print(row)
cursor.close()
conn.close()
