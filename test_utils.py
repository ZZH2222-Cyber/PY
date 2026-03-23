import sys
sys.path.append('src')

from utils.excel_utils import read_excel
from utils.db_utils import connect_db, query_db, close_db

def test_excel_read():
    """
    测试Excel读取功能
    """
    print("测试Excel读取功能...")
    try:
        data = read_excel('data/test_data.xlsx')
        print(f"读取到 {len(data)} 条数据")
        for item in data:
            print(item)
        print("Excel读取测试成功！")
    except Exception as e:
        print(f"Excel读取测试失败: {e}")

def test_db_connect():
    """
    测试数据库连接功能
    """
    print("\n测试数据库连接功能...")
    try:
        # 这里使用默认参数，实际使用时需要根据具体数据库配置修改
        conn = connect_db()
        print("数据库连接成功！")
        close_db(conn)
    except Exception as e:
        print(f"数据库连接测试失败: {e}")
        print("注意：如果本地没有MySQL数据库，可以跳过此测试")

if __name__ == "__main__":
    test_excel_read()
    test_db_connect()
