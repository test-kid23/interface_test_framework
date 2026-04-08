import requests
import time
import json
import allure
from allure_commons.types import AttachmentType
from libs.env_manager import env_manager
from libs.logger import logger

class RequestClient:
    def __init__(self):
        """初始化请求客户端"""
        self.session = requests.Session()
        self.base_url = env_manager.get_base_url()
        self.timeout = env_manager.get_timeout()
        # 添加环境公共headers
        self.session.headers.update(env_manager.get_headers())
        logger.info(f"请求客户端初始化完成，base_url: {self.base_url}, timeout: {self.timeout}")
    
    @allure.step("{method} {url}")
    def request(self, method, url, **kwargs):
        """发送请求，自动拼接 base_url，记录日志，返回 Response 对象"""
        # 拼接完整 URL
        if not url.startswith('http'):
            url = f"{self.base_url}{url}"
        
        # 设置超时
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        # 记录请求信息
        logger.info(f"发送请求: {method} {url}")
        logger.debug(f"请求头: {json.dumps(dict(self.session.headers), indent=2)}")
        if 'json' in kwargs:
            logger.debug(f"请求体: {json.dumps(kwargs['json'], indent=2)}")
        elif 'data' in kwargs:
            logger.debug(f"请求体: {kwargs['data']}")
        
        # 附加请求信息到 Allure 报告
        allure.attach(
            json.dumps({"method": method, "url": url, "kwargs": kwargs}, ensure_ascii=False, indent=2),
            name="请求信息",
            attachment_type=AttachmentType.TEXT
        )
        
        # 发送请求
        start_time = time.time()
        try:
            response = self.session.request(method, url, **kwargs)
            elapsed_time = time.time() - start_time
            
            # 记录响应信息
            logger.info(f"收到响应: {response.status_code}, 耗时: {elapsed_time:.3f}s")
            logger.debug(f"响应头: {json.dumps(dict(response.headers), indent=2)}")
            try:
                response_json = response.json()
                logger.debug(f"响应体: {json.dumps(response_json, indent=2)}")
            except:
                logger.debug(f"响应体: {response.text}")
            
            # 附加响应信息到 Allure 报告
            allure.attach(
                json.dumps({"status_code": response.status_code, "headers": dict(response.headers), "text": response.text}, ensure_ascii=False, indent=2),
                name="响应信息",
                attachment_type=AttachmentType.TEXT
            )
            
            return response
        except Exception as e:
            logger.error(f"请求失败: {e}")
            # 附加错误信息到 Allure 报告
            allure.attach(
                str(e),
                name="请求错误",
                attachment_type=AttachmentType.TEXT
            )
            raise
    
    def get(self, url, **kwargs):
        """发送 GET 请求"""
        return self.request('GET', url, **kwargs)
    
    def post(self, url, **kwargs):
        """发送 POST 请求"""
        return self.request('POST', url, **kwargs)
    
    def put(self, url, **kwargs):
        """发送 PUT 请求"""
        return self.request('PUT', url, **kwargs)
    
    def delete(self, url, **kwargs):
        """发送 DELETE 请求"""
        return self.request('DELETE', url, **kwargs)
    
    def close(self):
        """关闭会话"""
        self.session.close()
        logger.info("请求会话已关闭")

# 导出类
__all__ = ["RequestClient"]
