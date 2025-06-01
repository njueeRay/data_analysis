"""
小红书爬虫 - 专门爬取小红书平台的AI硬件相关内容
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

class XiaoHongShuCrawler(BaseCrawler):
    """
    小红书爬虫类 - 继承自BaseCrawler
    专门用于爬取小红书平台的AI硬件相关笔记和用户互动数据
    """
    
    def __init__(self):
        super().__init__('xiaohongshu')
        self.base_url = "https://www.xiaohongshu.com"
        self.search_url = "https://www.xiaohongshu.com/search_result"
        self.setup_xiaohongshu_headers()
        
    def setup_xiaohongshu_headers(self):
        """设置小红书特定的请求头"""
        self.session.headers.update({
            'Referer': 'https://www.xiaohongshu.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'X-Requested-With': 'XMLHttpRequest',
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
            'keyword': keyword,
            'page': page,
            'page_size': 20,
            'sort': 'general',  # 综合排序
            'note_type': 0      # 所有类型
        }
        
        url_params = '&'.join([f"{k}={quote(str(v))}" for k, v in params.items()])
        return f"{self.search_url}?{url_params}"
    
    def extract_engagement_data(self, note_data: Dict) -> Dict[str, int]:
        """
        提取用户互动数据
        
        Args:
            note_data: 笔记数据字典
            
        Returns:
            互动数据字典
        """
        engagement = {
            'likes': 0,
            'comments_count': 0,
            'shares': 0
        }
        
        try:
            # 提取点赞数
            if 'liked_count' in note_data:
                engagement['likes'] = int(note_data['liked_count'])
            elif 'interact_info' in note_data:
                interact_info = note_data['interact_info']
                engagement['likes'] = int(interact_info.get('liked_count', 0))
            
            # 提取评论数
            if 'comment_count' in note_data:
                engagement['comments_count'] = int(note_data['comment_count'])
            elif 'interact_info' in note_data:
                interact_info = note_data['interact_info']
                engagement['comments_count'] = int(interact_info.get('comment_count', 0))
            
            # 提取分享数（小红书通常不显示分享数，设为0）
            engagement['shares'] = 0
            
        except (ValueError, KeyError) as e:
            self.logger.warning(f"提取互动数据失败: {e}")
        
        return engagement
    
    def extract_user_info(self, note_data: Dict) -> Dict[str, str]:
        """
        提取用户信息
        
        Args:
            note_data: 笔记数据字典
            
        Returns:
            用户信息字典
        """
        user_info = {
            'user_id': '',
            'username': '',
            'user_level': ''
        }
        
        try:
            if 'user' in note_data:
                user = note_data['user']
                user_info['user_id'] = str(user.get('user_id', ''))
                user_info['username'] = user.get('nickname', '')
            
            # 提取用户等级信息（如果有）
            if 'user_level' in note_data:
                user_info['user_level'] = str(note_data['user_level'])
                
        except KeyError as e:
            self.logger.warning(f"提取用户信息失败: {e}")
        
        return user_info
    
    def extract_content_text(self, note_data: Dict) -> str:
        """
        提取笔记文本内容
        
        Args:
            note_data: 笔记数据字典
            
        Returns:
            清理后的文本内容
        """
        content = ""
        
        try:
            # 尝试不同的内容字段
            content_fields = ['desc', 'content', 'note_card', 'title']
            
            for field in content_fields:
                if field in note_data and note_data[field]:
                    if isinstance(note_data[field], str):
                        content = note_data[field]
                        break
                    elif isinstance(note_data[field], dict):
                        # 如果是字典，尝试提取text字段
                        if 'text' in note_data[field]:
                            content = note_data[field]['text']
                            break
            
            # 清理HTML标签和特殊字符
            if content:
                content = re.sub(r'<[^>]+>', '', content)  # 去除HTML标签
                content = re.sub(r'\s+', ' ', content).strip()  # 规范化空格
                
        except Exception as e:
            self.logger.warning(f"提取内容文本失败: {e}")
        
        return content
    
    def extract_tags(self, note_data: Dict) -> List[str]:
        """
        提取标签信息
        
        Args:
            note_data: 笔记数据字典
            
        Returns:
            标签列表
        """
        tags = []
        
        try:
            # 尝试不同的标签字段
            if 'tag_list' in note_data:
                tag_list = note_data['tag_list']
                if isinstance(tag_list, list):
                    for tag in tag_list:
                        if isinstance(tag, dict) and 'name' in tag:
                            tags.append(tag['name'])
                        elif isinstance(tag, str):
                            tags.append(tag)
            
            # 从内容中提取话题标签
            content = self.extract_content_text(note_data)
            if content:
                # 提取#话题#格式的标签
                topic_matches = re.findall(r'#([^#\s]+)#', content)
                tags.extend(topic_matches)
                
        except Exception as e:
            self.logger.warning(f"提取标签失败: {e}")
        
        return list(set(tags))  # 去重
    
    def parse_item(self, note_data: Dict) -> Dict[str, Any]:
        """
        解析单条笔记数据
        
        Args:
            note_data: 笔记原始数据字典
            
        Returns:
            标准化的笔记数据
        """
        try:
            # 提取基础信息
            title = note_data.get('display_title', '')
            content = self.extract_content_text(note_data)
            
            # 如果没有标题，使用内容的前50个字符作为标题
            if not title and content:
                title = content[:50] + "..." if len(content) > 50 else content
            
            # 提取互动数据
            engagement = self.extract_engagement_data(note_data)
            
            # 提取用户信息
            user_info = self.extract_user_info(note_data)
            
            # 提取标签
            tags = self.extract_tags(note_data)
            
            # 提取发布时间
            publish_time = note_data.get('time', '')
            if publish_time:
                try:
                    # 转换时间戳或时间字符串
                    if isinstance(publish_time, int):
                        publish_date = datetime.fromtimestamp(publish_time).strftime('%Y-%m-%d')
                    else:
                        publish_date = str(publish_time)[:10]  # 取前10个字符作为日期
                except:
                    publish_date = datetime.now().strftime('%Y-%m-%d')
            else:
                publish_date = datetime.now().strftime('%Y-%m-%d')
            
            # 提取笔记链接
            note_id = note_data.get('id', note_data.get('note_id', ''))
            source_url = f"https://www.xiaohongshu.com/explore/{note_id}" if note_id else ""
            
            # 构建原始数据
            raw_data = {
                'title': title,
                'content': content,
                'likes': engagement['likes'],
                'comments_count': engagement['comments_count'],
                'shares': engagement['shares'],
                'source_url': source_url,
                'publish_date': publish_date,
                'tags': tags,
                'product_type': self.classify_product(title, content),
                'user_id': user_info['user_id'],
                'username': user_info['username'],
                'price': 0,  # 小红书笔记通常不直接包含价格信息
                'sales': 0,  # 小红书笔记不包含销量信息
                'shop_name': '',  # 小红书笔记通常不是商品页面
                'location': ''   # 可以后续扩展提取位置信息
            }
            
            return self.standardize_data(raw_data)
            
        except Exception as e:
            self.logger.error(f"解析笔记数据失败: {e}")
            return {}
    
    def search(self, keyword: str, max_pages: int = 3) -> List[Dict[str, Any]]:
        """
        搜索小红书笔记
        
        Args:
            keyword: 搜索关键词
            max_pages: 最大搜索页数
            
        Returns:
            笔记信息列表
        """
        all_notes = []
        self.logger.info(f"开始搜索小红书关键词: {keyword}")
        
        for page in range(1, max_pages + 1):
            self.logger.info(f"正在爬取第 {page} 页...")
            
            # 构建搜索URL
            search_url = self.build_search_url(keyword, page)
            
            # 发送请求
            response = self.safe_request(search_url)
            if not response:
                self.logger.warning(f"第 {page} 页请求失败，跳过")
                continue
            
            try:
                # 小红书返回的可能是JSON数据
                if response.headers.get('content-type', '').startswith('application/json'):
                    data = response.json()
                    
                    # 根据小红书API结构提取笔记列表
                    notes_data = []
                    if 'data' in data:
                        if 'notes' in data['data']:
                            notes_data = data['data']['notes']
                        elif isinstance(data['data'], list):
                            notes_data = data['data']
                    
                else:
                    # 如果是HTML页面，尝试解析
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 查找包含笔记数据的script标签
                    script_tags = soup.find_all('script')
                    notes_data = []
                    
                    for script in script_tags:
                        if script.string and 'window.__INITIAL_STATE__' in script.string:
                            # 提取初始状态数据
                            try:
                                script_content = script.string
                                start_idx = script_content.find('{')
                                end_idx = script_content.rfind('}') + 1
                                json_str = script_content[start_idx:end_idx]
                                
                                initial_data = json.loads(json_str)
                                # 根据实际结构提取笔记数据
                                # 这部分需要根据小红书的实际页面结构调整
                                
                            except json.JSONDecodeError:
                                continue
                
                if not notes_data:
                    self.logger.warning(f"第 {page} 页未找到笔记数据")
                    # 保存HTML用于调试
                    with open(f'debug_xiaohongshu_page_{page}.html', 'w', encoding='utf-8') as f:
                        f.write(response.text[:5000])
                    continue
                
                self.logger.info(f"第 {page} 页找到 {len(notes_data)} 条笔记")
                
                # 解析每条笔记
                page_notes = []
                for note_data in notes_data:
                    try:
                        parsed_note = self.parse_item(note_data)
                        if parsed_note and self.validate_data(parsed_note):
                            page_notes.append(parsed_note)
                    except Exception as e:
                        self.logger.error(f"解析笔记失败: {e}")
                        continue
                
                all_notes.extend(page_notes)
                self.logger.info(f"第 {page} 页成功解析 {len(page_notes)} 条笔记")
                
            except Exception as e:
                self.logger.error(f"处理第 {page} 页数据失败: {e}")
                continue
            
            # 添加页面间延时
            if page < max_pages:
                time.sleep(3)
        
        self.logger.info(f"搜索完成，总共获取 {len(all_notes)} 条笔记")
        return all_notes
    
    def crawl_all_keywords(self, max_pages_per_keyword: int = 2) -> List[Dict[str, Any]]:
        """
        爬取所有配置的关键词
        
        Args:
            max_pages_per_keyword: 每个关键词的最大页数
            
        Returns:
            所有笔记数据列表
        """
        all_data = []
        
        # 获取适合小红书的关键词（偏向用户体验和评测）
        xiaohongshu_keywords = (
            SEARCH_KEYWORDS['primary'][:5] +  # 前5个主要关键词
            ['AI音箱评测', 'AI陪伴机器人', '智能助手使用感受', '二次元AI']  # 小红书特色关键词
        )
        
        self.logger.info(f"开始爬取 {len(xiaohongshu_keywords)} 个关键词")
        
        for i, keyword in enumerate(xiaohongshu_keywords, 1):
            self.logger.info(f"[{i}/{len(xiaohongshu_keywords)}] 爬取关键词: {keyword}")
            
            try:
                keyword_data = self.search(keyword, max_pages_per_keyword)
                all_data.extend(keyword_data)
                self.logger.info(f"关键词 '{keyword}' 获取 {len(keyword_data)} 条数据")
                
                # 关键词间休息
                if i < len(xiaohongshu_keywords):
                    time.sleep(5)  # 小红书需要更长的间隔
                    
            except Exception as e:
                self.logger.error(f"爬取关键词 '{keyword}' 失败: {e}")
                continue
        
        self.logger.info(f"所有关键词爬取完成，共获取 {len(all_data)} 条数据")
        return all_data

def main():
    """主函数 - 运行小红书爬虫"""
    crawler = XiaoHongShuCrawler()
    
    # 爬取所有关键词数据
    all_data = crawler.crawl_all_keywords(max_pages_per_keyword=2)
    
    if all_data:
        # 保存数据
        filename = f"xiaohongshu_{datetime.now().strftime('%Y%m%d_%H%M%S')}_raw.csv"
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