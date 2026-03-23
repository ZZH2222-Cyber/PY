import pymysql

def connect_db(host='localhost', port=3306, user='root', password='', db='test'):
    """
    连接数据库
    
    Args:
        host: 数据库主机
        port: 数据库端口
        user: 数据库用户名
        password: 数据库密码
        db: 数据库名称
    
    Returns:
        pymysql.Connection: 数据库连接对象
    """
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        db=db,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def query_db(conn, sql, params=None):
    """
    执行SQL查询
    
    Args:
        conn: 数据库连接对象
        sql: SQL查询语句
        params: SQL参数
    
    Returns:
        list: 查询结果列表
    """
    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        result = cursor.fetchall()
    return result

def close_db(conn):
    """
    关闭数据库连接
    
    Args:
        conn: 数据库连接对象
    """
    if conn:
        conn.close()
