import requests
import json

# 测试API接口
url = 'http://127.0.0.1:5000/api/test'
headers = {'Content-Type': 'application/json'}
data = {
    'base_url': 'https://httpbin.org',
    'endpoint': '/get',
    'method': 'GET',
    'headers': {'Content-Type': 'application/json'},
    'body': {}
}

print('测试API接口...')
print(f'URL: {url}')
print(f'Data: {json.dumps(data, indent=2)}')

response = requests.post(url, json=data, headers=headers)

print(f'\n响应状态码: {response.status_code}')
print(f'响应内容: {response.text}')