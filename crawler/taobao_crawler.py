"""
淘宝爬虫 - 专门爬取淘宝平台的AI硬件产品数据
"""

import re
import json
import time
from typing import Dict, List, Any, Optional
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crawler.base_crawler import BaseCrawler
from config import SEARCH_KEYWORDS, PRODUCT_CATEGORIES

class TaobaoCrawler(BaseCrawler):
    """
    淘宝爬虫类 - 继承自BaseCrawler
    专门用于爬取淘宝平台的AI硬件产品信息
    """
    
    def __init__(self):
        super().__init__('taobao')
        self.base_url = "https://s.taobao.com/search"
        self.setup_taobao_headers()
        
    def setup_taobao_headers(self):
        """设置淘宝特定的请求头"""
        self.session.headers.update({
            'Referer': 'https://www.taobao.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def build_search_url(self, keyword: str, page: int = 1) -> str:
        """
        构建搜索URL
        
        Args:
            keyword: 搜索关键词
            page: 页码
            
        Returns:
            完整的搜索URL
        """
        params = {
            'q': keyword,
            's': (page - 1) * 44,  # 淘宝每页44个商品
            'sort': 'sale-desc',   # 按销量排序
        }
        
        url_params = '&'.join([f"{k}={quote(str(v))}" for k, v in params.items()])
        return f"{self.base_url}?{url_params}"
    
    def extract_price(self, price_text: str) -> Optional[float]:
        """
        提取并清理价格信息
        
        Args:
            price_text: 价格文本
            
        Returns:
            清理后的价格数值
        """
        if not price_text:
            return None
            
        # 使用正则表达式提取数字
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        if price_match:
            try:
                return float(price_match.group())
            except ValueError:
                return None
        return None
    
    def extract_sales(self, sales_text: str) -> Optional[int]:
        """
        提取销量信息
        
        Args:
            sales_text: 销量文本
            
        Returns:
            销量数值
        """
        if not sales_text:
            return None
            
        # 处理销量格式：1000+人付款，5万+人付款等
        sales_text = sales_text.replace('人付款', '').replace('+', '').replace('万', '0000')
        
        # 提取数字
        sales_match = re.search(r'\d+', sales_text)
        if sales_match:
            try:
                return int(sales_match.group())
            except ValueError:
                return None
        return None
    
    def classify_product(self, title: str, content: str = "") -> str:
        """
        根据标题和内容对产品进行分类
        
        Args:
            title: 商品标题
            content: 商品描述
            
        Returns:
            产品分类
        """
        text = (title + " " + content).lower()
        
        for category, keywords in PRODUCT_CATEGORIES.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    return category
                    
        return "其他AI产品"
    
    def parse_item(self, item_element) -> Dict[str, Any]:
        """
        解析单个商品信息
        
        Args:
            item_element: BeautifulSoup商品元素
            
        Returns:
            标准化的商品数据
        """
        try:
            # 提取标题
            title_elem = item_element.find('a', class_='title')
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # 提取价格
            price_elem = item_element.find('span', class_='price')
            price_text = price_elem.get_text(strip=True) if price_elem else ""
            price = self.extract_price(price_text)
            
            # 提取销量
            sales_elem = item_element.find('span', class_='deal-cnt')
            sales_text = sales_elem.get_text(strip=True) if sales_elem else ""
            sales = self.extract_sales(sales_text)
            
            # 提取商品链接
            link_elem = item_element.find('a', class_='title')
            product_url = link_elem.get('href') if link_elem else ""
            if product_url and not product_url.startswith('http'):
                product_url = 'https:' + product_url
            
            # 提取店铺信息
            shop_elem = item_element.find('a', class_='shopname')
            shop_name = shop_elem.get_text(strip=True) if shop_elem else ""
            
            # 提取位置信息
            location_elem = item_element.find('span', class_='location')
            location = location_elem.get_text(strip=True) if location_elem else ""
            
            # 构建原始数据
            raw_data = {
                'title': title,
                'content': title,  # 淘宝商品以标题为主要内容
                'price': price,
                'sales': sales,
                'shop_name': shop_name,
                'location': location,
                'source_url': product_url,
                'product_type': self.classify_product(title),
                'likes': 0,  # 淘宝没有点赞概念，设为0
                'comments_count': 0,  # 评论数需要进入详情页获取，此处设为0
                'shares': 0,  # 淘宝没有分享概念，设为0
                'publish_date': datetime.now().strftime('%Y-%m-%d'),  # 爬取日期
                'tags': [self.classify_product(title)],
            }
            
            return self.standardize_data(raw_data)
            
        except Exception as e:
            self.logger.error(f"解析商品信息失败: {e}")
            return {}
    
    def search(self, keyword: str, max_pages: int = 3) -> List[Dict[str, Any]]:
        """
        搜索淘宝商品
        
        Args:
            keyword: 搜索关键词
            max_pages: 最大搜索页数
            
        Returns:
            商品信息列表
        """
        all_products = []
        self.logger.info(f"开始搜索淘宝关键词: {keyword}")
        
        for page in range(1, max_pages + 1):
            self.logger.info(f"正在爬取第 {page} 页...")
            
            # 构建搜索URL
            search_url = self.build_search_url(keyword, page)
            
            # 发送请求
            response = self.safe_request(search_url)
            if not response:
                self.logger.warning(f"第 {page} 页请求失败，跳过")
                continue
            
            # 解析页面
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找商品列表
            # 淘宝的商品容器可能有多种class名
            item_selectors = [
                'div[data-category="auctions"]',
                '.item',
                '.ctx-box',
                '[data-auction]'
            ]
            
            items = []
            for selector in item_selectors:
                items = soup.select(selector)
                if items:
                    break
            
            if not items:
                self.logger.warning(f"第 {page} 页未找到商品，可能需要调整选择器")
                # 保存HTML用于调试
                with open(f'debug_taobao_page_{page}.html', 'w', encoding='utf-8') as f:
                    f.write(response.text[:5000])  # 保存前5000字符
                continue
            
            self.logger.info(f"第 {page} 页找到 {len(items)} 个商品")
            
            # 解析每个商品
            page_products = []
            for item in items:
                try:
                    product_data = self.parse_item(item)
                    if product_data and self.validate_data(product_data):
                        page_products.append(product_data)
                except Exception as e:
                    self.logger.error(f"解析商品失败: {e}")
                    continue
            
            all_products.extend(page_products)
            self.logger.info(f"第 {page} 页成功解析 {len(page_products)} 个商品")
            
            # 添加页面间延时
            if page < max_pages:
                time.sleep(2)
        
        self.logger.info(f"搜索完成，总共获取 {len(all_products)} 个商品")
        return all_products
    
    def crawl_all_keywords(self, max_pages_per_keyword: int = 2) -> List[Dict[str, Any]]:
        """
        爬取所有配置的关键词
        
        Args:
            max_pages_per_keyword: 每个关键词的最大页数
            
        Returns:
            所有商品数据列表
        """
        all_data = []
        
        # 获取所有关键词
        all_keywords = (
            SEARCH_KEYWORDS['primary'] + 
            SEARCH_KEYWORDS['secondary'] + 
            SEARCH_KEYWORDS['brands']
        )
        
        self.logger.info(f"开始爬取 {len(all_keywords)} 个关键词")
        
        for i, keyword in enumerate(all_keywords, 1):
            self.logger.info(f"[{i}/{len(all_keywords)}] 爬取关键词: {keyword}")
            
            try:
                keyword_data = self.search(keyword, max_pages_per_keyword)
                all_data.extend(keyword_data)
                self.logger.info(f"关键词 '{keyword}' 获取 {len(keyword_data)} 条数据")
                
                # 关键词间休息
                if i < len(all_keywords):
                    time.sleep(3)
                    
            except Exception as e:
                self.logger.error(f"爬取关键词 '{keyword}' 失败: {e}")
                continue
        
        self.logger.info(f"所有关键词爬取完成，共获取 {len(all_data)} 条数据")
        return all_data

def main():
    """主函数 - 运行淘宝爬虫"""
    crawler = TaobaoCrawler()
    
    # 爬取所有关键词数据
    all_data = crawler.crawl_all_keywords(max_pages_per_keyword=2)
    
    if all_data:
        # 保存数据
        filename = f"taobao_{datetime.now().strftime('%Y%m%d_%H%M%S')}_raw.csv"
        crawler.save_data(all_data, filename)
        
        # 输出统计信息
        stats = crawler.get_stats(all_data)
        print("\n=== 爬取统计 ===")
        for key, value in stats.items():
            print(f"{key}: {value}")
    else:
        print("未获取到任何数据")

if __name__ == "__main__":
    main() 