"""
基础爬虫类 - 提供通用的爬虫功能和接口规范
"""

import time
import random
import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CRAWLER_CONFIG, PLATFORMS, DATA_SCHEMA

class BaseCrawler(ABC):
    """
    基础爬虫类，定义所有平台爬虫的通用接口和功能
    """
    
    def __init__(self, platform_name: str):
        """
        初始化爬虫
        
        Args:
            platform_name: 平台名称 (xiaohongshu/douyin/taobao)
        """
        self.platform_name = platform_name
        self.platform_config = PLATFORMS.get(platform_name, {})
        self.crawler_config = CRAWLER_CONFIG
        self.session = requests.Session()
        self.setup_session()
        self.setup_logging()
        
    def setup_session(self):
        """配置请求会话"""
        # 设置默认headers
        self.session.headers.update({
            'User-Agent': random.choice(self.crawler_config['user_agents']),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # 设置超时
        self.session.timeout = self.crawler_config['timeout']
        
    def setup_logging(self):
        """设置日志"""
        self.logger = logging.getLogger(f"{self.platform_name}_crawler")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def random_delay(self):
        """随机延时，避免请求过于频繁"""
        delay = random.uniform(*self.crawler_config['delay_range'])
        time.sleep(delay)
        
    def safe_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        安全的HTTP请求，包含重试机制
        
        Args:
            url: 请求URL
            **kwargs: requests参数
            
        Returns:
            Response对象或None
        """
        for attempt in range(self.crawler_config['max_retries']):
            try:
                self.random_delay()
                
                # 随机更换User-Agent
                headers = kwargs.get('headers', {})
                headers['User-Agent'] = random.choice(self.crawler_config['user_agents'])
                kwargs['headers'] = headers
                
                response = self.session.get(url, **kwargs)
                
                if response.status_code == 200:
                    self.logger.info(f"成功请求: {url}")
                    return response
                else:
                    self.logger.warning(f"请求失败 {response.status_code}: {url}")
                    
            except Exception as e:
                self.logger.error(f"请求异常 (尝试 {attempt + 1}/{self.crawler_config['max_retries']}): {e}")
                
            if attempt < self.crawler_config['max_retries'] - 1:
                wait_time = (attempt + 1) * 2  # 递增等待时间
                self.logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
                
        self.logger.error(f"请求最终失败: {url}")
        return None
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        验证数据完整性
        
        Args:
            data: 要验证的数据字典
            
        Returns:
            是否有效
        """
        # 检查必需字段
        for field in DATA_SCHEMA['required_fields']:
            if field not in data or not data[field]:
                self.logger.warning(f"缺失必需字段: {field}")
                return False
                
        return True
    
    def standardize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化数据格式
        
        Args:
            raw_data: 原始数据
            
        Returns:
            标准化后的数据
        """
        standardized = {
            'platform': self.platform_config.get('name', self.platform_name),
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        # 映射和清理数据
        for field in DATA_SCHEMA['required_fields'] + DATA_SCHEMA['optional_fields']:
            if field in raw_data:
                standardized[field] = raw_data[field]
            elif field not in ['platform', 'crawl_time']:
                standardized[field] = None
                
        return standardized
    
    @abstractmethod
    def search(self, keyword: str, max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        搜索方法 - 必须在子类中实现
        
        Args:
            keyword: 搜索关键词
            max_pages: 最大页数
            
        Returns:
            搜索结果列表
        """
        pass
    
    @abstractmethod
    def parse_item(self, item_html: str) -> Dict[str, Any]:
        """
        解析单个商品/内容 - 必须在子类中实现
        
        Args:
            item_html: 商品HTML内容
            
        Returns:
            解析后的数据字典
        """
        pass
    
    def save_data(self, data_list: List[Dict[str, Any]], filename: str):
        """
        保存数据到文件
        
        Args:
            data_list: 数据列表
            filename: 保存文件名
        """
        import pandas as pd
        from pathlib import Path
        
        if not data_list:
            self.logger.warning("没有数据需要保存")
            return
            
        # 创建DataFrame
        df = pd.DataFrame(data_list)
        
        # 保存路径
        save_path = Path("raw_data") / filename
        save_path.parent.mkdir(exist_ok=True)
        
        # 保存为CSV
        df.to_csv(save_path, index=False, encoding='utf-8-sig')
        self.logger.info(f"数据已保存到: {save_path}")
        self.logger.info(f"共保存 {len(data_list)} 条数据")
        
    def get_stats(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取数据统计信息
        
        Args:
            data_list: 数据列表
            
        Returns:
            统计信息字典
        """
        if not data_list:
            return {"总数": 0}
            
        stats = {
            "总数": len(data_list),
            "平台": self.platform_config.get('name', self.platform_name),
            "爬取时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 统计有效数据
        valid_count = sum(1 for item in data_list if self.validate_data(item))
        stats["有效数据"] = valid_count
        stats["有效率"] = f"{valid_count/len(data_list)*100:.1f}%" if len(data_list) > 0 else "0%"
        
        return stats 