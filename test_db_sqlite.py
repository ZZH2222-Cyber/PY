import sqlite3

# 连接SQLite数据库
def connect_db(db_path='test.db'):
    """
    连接到SQLite数据库
    
    Args:
        db_path: 数据库文件路径
    
    Returns:
        sqlite3.Connection: 数据库连接对象
    """
    return sqlite3.connect(db_path)

# 执行数据库查询
def query_db(conn, sql, params=None):
    """
    执行SQL查询
    
    Args:
        conn: 数据库连接对象
        sql: SQL查询语句
        params: 查询参数
    
    Returns:
        list: 查询结果
    """
    cursor = conn.cursor()
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    return cursor.fetchall()

# 测试数据库功能
def test_db_functionality():
    print("=== 连接SQLite数据库 ===")
    try:
        # 连接数据库
        conn = connect_db()
        print("数据库连接成功")

        # 执行查询
        print("\n=== 执行数据库查询 ===")
        sql = "SELECT * FROM users LIMIT 5"
        results = query_db(conn, sql)
        print("查询结果:")
        for row in results:
            print(row)

        # 执行带参数的查询
        print("\n=== 执行带参数的查询 ===")
        sql = "SELECT * FROM users WHERE age > ?"
        params = (25,)
        results = query_db(conn, sql, params)
        print("年龄大于25的用户:")
        for row in results:
            print(row)

        # 关闭连接
        conn.close()
        print("\n数据库连接已关闭")
    except Exception as e:
        print(f"\n数据库操作失败: {str(e)}")

if __name__ == "__main__":
    test_db_functionality()
