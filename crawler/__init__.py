"""
AI硬件分析项目 - 爬虫模块
包含小红书、抖音、淘宝三大平台的数据采集功能
"""

from .base_crawler import BaseCrawler
from .taobao_crawler import TaobaoCrawler
from .xiaohongshu_crawler import XiaoHongShuCrawler
from .data_validator import DataValidator

__version__ = "1.0.0"
__all__ = ["BaseCrawler", "TaobaoCrawler", "XiaoHongShuCrawler", "DataValidator"] 