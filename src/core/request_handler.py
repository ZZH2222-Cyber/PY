import requests
import logging
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RequestHandler:
    """
    HTTP请求处理器，封装requests库，提供统一的请求方法
    """
    
    def __init__(self):
        self.session = requests.Session()
    
    def request(self, method, url, **kwargs):
        """
        发送HTTP请求
        
        Args:
            method: 请求方法（GET, POST, PUT, DELETE等）
            url: 请求URL
            **kwargs: 其他请求参数
        
        Returns:
            requests.Response: 响应对象
        """
        start_time = time.time()
        logger.info(f"发送{method}请求到 {url}")
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()  # 自动处理4xx和5xx错误
            elapsed_time = time.time() - start_time
            logger.info(f"请求成功，状态码: {response.status_code}，耗时: {elapsed_time:.2f}s")
            return response
        except requests.exceptions.RequestException as e:
            elapsed_time = time.time() - start_time
            logger.error(f"请求失败，耗时: {elapsed_time:.2f}s，错误: {str(e)}")
            raise
    
    def get(self, url, **kwargs):
        """
        发送GET请求
        
        Args:
            url: 请求URL
            **kwargs: 其他请求参数
        
        Returns:
            requests.Response: 响应对象
        """
        return self.request('GET', url, **kwargs)
    
    def post(self, url, **kwargs):
        """
        发送POST请求
        
        Args:
            url: 请求URL
            **kwargs: 其他请求参数
        
        Returns:
            requests.Response: 响应对象
        """
        return self.request('POST', url, **kwargs)
    
    def put(self, url, **kwargs):
        """
        发送PUT请求
        
        Args:
            url: 请求URL
            **kwargs: 其他请求参数
        
        Returns:
            requests.Response: 响应对象
        """
        return self.request('PUT', url, **kwargs)
    
    def delete(self, url, **kwargs):
        """
        发送DELETE请求
        
        Args:
            url: 请求URL
            **kwargs: 其他请求参数
        
        Returns:
            requests.Response: 响应对象
        """
        return self.request('DELETE', url, **kwargs)
    
    def close(self):
        """
        关闭会话
        """
        self.session.close()
