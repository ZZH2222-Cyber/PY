from src.utils.db_utils import connect_db, query_db

# 连接数据库（使用测试数据库）
try:
    print("=== 连接数据库 ===")
    conn = connect_db(host='localhost', user='root', password='', db='test')
    print("数据库连接成功")

    # 执行查询
    print("\n=== 执行数据库查询 ===")
    sql = "SELECT * FROM users LIMIT 5"
    results = query_db(conn, sql)
    print("查询结果:", results)

    # 关闭连接
    conn.close()
    print("\n数据库连接已关闭")
except Exception as e:
    print(f"\n数据库操作失败: {str(e)}")
    print("注意：此演示需要本地安装MySQL并创建test数据库")
