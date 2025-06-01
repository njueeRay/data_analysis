"""
爬虫管理器 - 统一管理三个平台的数据采集
"""

import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crawler.taobao_crawler import TaobaoCrawler
from crawler.xiaohongshu_crawler import XiaoHongShuCrawler
from crawler.data_validator import DataValidator
from config import PLATFORMS

class CrawlerManager:
    """
    爬虫管理器
    负责协调三个平台的数据采集，数据整合和质量控制
    """
    
    def __init__(self):
        self.validator = DataValidator()
        self.crawlers = {}
        self.setup_logging()
        self.initialize_crawlers()
        
    def setup_logging(self):
        """设置日志系统"""
        self.logger = logging.getLogger('CrawlerManager')
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def initialize_crawlers(self):
        """初始化所有爬虫"""
        try:
            self.crawlers['taobao'] = TaobaoCrawler()
            self.logger.info("✅ 淘宝爬虫初始化成功")
        except Exception as e:
            self.logger.error(f"❌ 淘宝爬虫初始化失败: {e}")
            
        try:
            self.crawlers['xiaohongshu'] = XiaoHongShuCrawler()
            self.logger.info("✅ 小红书爬虫初始化成功")
        except Exception as e:
            self.logger.error(f"❌ 小红书爬虫初始化失败: {e}")
            
        # 抖音爬虫待实现
        # try:
        #     self.crawlers['douyin'] = DouyinCrawler()
        #     self.logger.info("✅ 抖音爬虫初始化成功")
        # except Exception as e:
        #     self.logger.error(f"❌ 抖音爬虫初始化失败: {e}")
    
    def crawl_platform(self, platform: str, max_pages_per_keyword: int = 2) -> List[Dict[str, Any]]:
        """
        爬取单个平台数据
        
        Args:
            platform: 平台名称 (taobao/xiaohongshu/douyin)
            max_pages_per_keyword: 每个关键词的最大页数
            
        Returns:
            平台数据列表
        """
        if platform not in self.crawlers:
            self.logger.error(f"平台 {platform} 的爬虫未初始化")
            return []
        
        self.logger.info(f"开始爬取 {platform} 平台数据...")
        start_time = time.time()
        
        try:
            crawler = self.crawlers[platform]
            data = crawler.crawl_all_keywords(max_pages_per_keyword)
            
            # 数据验证和清理
            if data:
                validated_data = self.validator.clean_dataset(data)
                end_time = time.time()
                
                self.logger.info(f"{platform} 平台爬取完成:")
                self.logger.info(f"  原始数据: {len(data)} 条")
                self.logger.info(f"  有效数据: {len(validated_data)} 条")
                self.logger.info(f"  耗时: {end_time - start_time:.2f} 秒")
                
                return validated_data
            else:
                self.logger.warning(f"{platform} 平台未获取到数据")
                return []
                
        except Exception as e:
            self.logger.error(f"爬取 {platform} 平台失败: {e}")
            return []
    
    def crawl_all_platforms(self, max_pages_per_keyword: int = 2, use_parallel: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """
        爬取所有平台数据
        
        Args:
            max_pages_per_keyword: 每个关键词的最大页数
            use_parallel: 是否使用并行爬取
            
        Returns:
            平台数据字典
        """
        self.logger.info("开始全平台数据采集...")
        start_time = time.time()
        
        platform_data = {}
        
        if use_parallel:
            # 并行爬取（注意：可能增加被反爬的风险）
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = {
                    executor.submit(self.crawl_platform, platform, max_pages_per_keyword): platform
                    for platform in self.crawlers.keys()
                }
                
                for future in as_completed(futures):
                    platform = futures[future]
                    try:
                        data = future.result()
                        platform_data[platform] = data
                    except Exception as e:
                        self.logger.error(f"并行爬取 {platform} 失败: {e}")
                        platform_data[platform] = []
        else:
            # 串行爬取（推荐，更安全）
            for platform in self.crawlers.keys():
                platform_data[platform] = self.crawl_platform(platform, max_pages_per_keyword)
                
                # 平台间休息，避免过于频繁的请求
                if len(self.crawlers) > 1:
                    self.logger.info("平台间休息 30 秒...")
                    time.sleep(30)
        
        end_time = time.time()
        total_data = sum(len(data) for data in platform_data.values())
        
        self.logger.info("="*50)
        self.logger.info("全平台爬取完成统计:")
        for platform, data in platform_data.items():
            self.logger.info(f"  {platform}: {len(data)} 条数据")
        self.logger.info(f"总数据量: {total_data} 条")
        self.logger.info(f"总耗时: {end_time - start_time:.2f} 秒")
        self.logger.info("="*50)
        
        return platform_data
    
    def merge_platform_data(self, platform_data: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        合并多平台数据
        
        Args:
            platform_data: 平台数据字典
            
        Returns:
            合并后的数据列表
        """
        merged_data = []
        
        for platform, data in platform_data.items():
            for item in data:
                # 确保每条数据都有平台标识
                item['platform'] = PLATFORMS.get(platform, {}).get('name', platform)
                merged_data.append(item)
        
        self.logger.info(f"数据合并完成，总计 {len(merged_data)} 条")
        return merged_data
    
    def save_platform_data(self, platform_data: Dict[str, List[Dict[str, Any]]], timestamp: str = None):
        """
        保存平台数据到文件
        
        Args:
            platform_data: 平台数据字典
            timestamp: 时间戳字符串，如不提供则自动生成
        """
        if not timestamp:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存单个平台数据
        for platform, data in platform_data.items():
            if data:
                filename = f"{platform}_{timestamp}_raw.csv"
                crawler = self.crawlers.get(platform)
                if crawler:
                    crawler.save_data(data, filename)
        
        # 保存合并数据
        merged_data = self.merge_platform_data(platform_data)
        if merged_data:
            import pandas as pd
            from pathlib import Path
            
            merged_filename = f"all_platforms_{timestamp}_merged.csv"
            save_path = Path("raw_data") / merged_filename
            save_path.parent.mkdir(exist_ok=True)
            
            df = pd.DataFrame(merged_data)
            df.to_csv(save_path, index=False, encoding='utf-8-sig')
            self.logger.info(f"合并数据已保存到: {save_path}")
    
    def generate_crawl_report(self, platform_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        生成爬取报告
        
        Args:
            platform_data: 平台数据字典
            
        Returns:
            爬取报告字典
        """
        report = {
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'platforms': {},
            'summary': {}
        }
        
        total_count = 0
        for platform, data in platform_data.items():
            platform_report = self.validator.validate_dataset(data)
            platform_report['platform_name'] = PLATFORMS.get(platform, {}).get('name', platform)
            report['platforms'][platform] = platform_report
            total_count += len(data)
        
        # 生成总结
        report['summary'] = {
            'total_platforms': len(platform_data),
            'total_data_count': total_count,
            'active_platforms': len([p for p, d in platform_data.items() if d]),
            'avg_data_per_platform': total_count / len(platform_data) if platform_data else 0
        }
        
        return report
    
    def print_crawl_report(self, report: Dict[str, Any]):
        """打印爬取报告"""
        print("\n" + "="*60)
        print("AI硬件分析项目 - 数据采集报告")
        print("="*60)
        print(f"采集时间: {report['crawl_time']}")
        print(f"总平台数: {report['summary']['total_platforms']}")
        print(f"活跃平台数: {report['summary']['active_platforms']}")
        print(f"总数据量: {report['summary']['total_data_count']} 条")
        print(f"平均每平台: {report['summary']['avg_data_per_platform']:.1f} 条")
        
        print("\n各平台详情:")
        print("-" * 60)
        for platform, platform_report in report['platforms'].items():
            print(f"{platform_report['platform_name']}:")
            print(f"  总数: {platform_report['总数']} 条")
            print(f"  有效数: {platform_report['有效数']} 条")
            print(f"  有效率: {platform_report['有效率']}")
            if platform_report['错误统计']:
                print(f"  主要错误: {list(platform_report['错误统计'].keys())[:3]}")
        
        print("="*60)

def main():
    """主函数 - 运行爬虫管理器"""
    manager = CrawlerManager()
    
    # 爬取所有平台数据
    platform_data = manager.crawl_all_platforms(
        max_pages_per_keyword=2,
        use_parallel=False  # 推荐使用串行模式，更安全
    )
    
    # 保存数据
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    manager.save_platform_data(platform_data, timestamp)
    
    # 生成和打印报告
    report = manager.generate_crawl_report(platform_data)
    manager.print_crawl_report(report)

if __name__ == "__main__":
    main() 