import openpyxl

# 创建一个新的工作簿
wb = openpyxl.Workbook()
ws = wb.active

# 设置表头
ws.append(['ID', 'Name', 'Age', 'Email'])

# 添加测试数据
ws.append([1, 'Alice', 25, 'alice@example.com'])
ws.append([2, 'Bob', 30, 'bob@example.com'])
ws.append([3, 'Charlie', 35, 'charlie@example.com'])

# 保存文件
wb.save('data/test_data.xlsx')
print('测试Excel文件已创建成功！')
