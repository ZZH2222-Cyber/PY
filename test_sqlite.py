import sqlite3

# 创建SQLite数据库连接
def create_sqlite_db():
    print("=== 创建SQLite数据库 ===")
    # 连接到SQLite数据库（如果不存在则创建）
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    # 创建users表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        email TEXT UNIQUE
    )
    ''')
    
    # 插入测试数据
    test_data = [
        ('Alice', 25, 'alice@example.com'),
        ('Bob', 30, 'bob@example.com'),
        ('Charlie', 35, 'charlie@example.com'),
        ('David', 28, 'david@example.com'),
        ('Eve', 22, 'eve@example.com')
    ]
    
    # 先清空表
    cursor.execute('DELETE FROM users')
    # 插入数据
    cursor.executemany('INSERT INTO users (name, age, email) VALUES (?, ?, ?)', test_data)
    
    # 提交事务
    conn.commit()
    print("数据库创建成功，测试数据已插入")
    
    # 关闭连接
    conn.close()

# 测试数据库查询
def test_sqlite_query():
    print("\n=== 测试SQLite数据库查询 ===")
    # 连接到SQLite数据库
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    # 执行查询
    cursor.execute('SELECT * FROM users LIMIT 5')
    results = cursor.fetchall()
    
    print("查询结果:")
    for row in results:
        print(row)
    
    # 关闭连接
    conn.close()

# 模拟db_utils模块的功能
def mock_db_utils():
    print("\n=== 模拟db_utils模块功能 ===")
    # 连接到SQLite数据库
    conn = sqlite3.connect('test.db')
    
    # 模拟query_db函数
    def query_db(conn, sql, params=None):
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return cursor.fetchall()
    
    # 测试查询
    sql = "SELECT * FROM users WHERE age > ?"
    params = (25,)
    results = query_db(conn, sql, params)
    
    print("年龄大于25的用户:")
    for row in results:
        print(row)
    
    # 关闭连接
    conn.close()

if __name__ == "__main__":
    create_sqlite_db()
    test_sqlite_query()
    mock_db_utils()
    print("\nSQLite数据库测试完成")
