"""
AI硬件分析项目配置文件
包含项目的核心配置参数、路径定义和常量设置
"""

import os
from pathlib import Path

# ========== 项目路径配置 ==========
PROJECT_ROOT = Path(__file__).parent.absolute()
RAW_DATA_DIR = PROJECT_ROOT / "raw_data"
CLEANED_DATA_DIR = PROJECT_ROOT / "cleaned_data"
VISUALIZATION_DIR = PROJECT_ROOT / "visualizations_output"
REPORT_DIR = PROJECT_ROOT / "report"

# 确保目录存在
for dir_path in [RAW_DATA_DIR, CLEANED_DATA_DIR, VISUALIZATION_DIR, REPORT_DIR]:
    dir_path.mkdir(exist_ok=True)

# ========== 平台配置 ==========
PLATFORMS = {
    'xiaohongshu': {
        'name': '小红书',
        'color': '#FF2442',  # 小红书品牌色
        'base_url': 'https://www.xiaohongshu.com',
        'search_path': '/search_result'
    },
    'douyin': {
        'name': '抖音',
        'color': '#000000',  # 抖音黑色
        'base_url': 'https://www.douyin.com',
        'search_path': '/search'
    },
    'taobao': {
        'name': '淘宝',
        'color': '#FF4400',  # 淘宝橙色
        'base_url': 'https://s.taobao.com',
        'search_path': '/search'
    }
}

# ========== 搜索关键词配置 ==========
SEARCH_KEYWORDS = {
    'primary': [
        'AI陪伴', '智能陪伴', '虚拟女友', '虚拟男友',
        '宠物机器人', '陪伴机器人', '智能音箱'
    ],
    'secondary': [
        '二次元', '动漫手办', '语音助手', 'AI玩偶', 
        '智能玩具', '语音陪伴', 'AI女友', 'AI伴侣'
    ],
    'brands': [
        '小爱同学', '天猫精灵', '小度', '若琪', 
        'Alexa', '小米音箱', '华为音箱'
    ]
}

# ========== 产品分类配置 ==========
PRODUCT_CATEGORIES = {
    'AI音箱': ['智能音箱', '语音助手', '小爱同学', '天猫精灵', '小度'],
    '陪伴机器人': ['宠物机器人', '陪伴机器人', 'AI狗', 'AI猫', '智能宠物'],
    '虚拟伴侣': ['虚拟女友', '虚拟男友', 'AI女友', 'AI伴侣'],
    '二次元手办': ['智能手办', '会说话的手办', '语音手办', '动漫机器人'],
    'AI玩具': ['智能玩具', 'AI玩偶', '会聊天的玩具']
}

# ========== 情感分析配置 ==========
SENTIMENT_CONFIG = {
    'positive_threshold': 0.6,
    'negative_threshold': 0.4,
    'positive_words': [
        '可爱', '萌', '治愈', '温暖', '陪伴', '有趣', '智能', 
        '好用', '实用', '值得', '推荐', '满意', '喜欢', '爱了'
    ],
    'negative_words': [
        '无聊', '鸡肋', '失望', '后悔', '坑', '垃圾', '难用',
        '卡顿', '反应慢', '声音难听', '不值', '浪费钱'
    ]
}

# ========== 爬虫配置 ==========
CRAWLER_CONFIG = {
    'delay_range': (0.5, 3.0),  # 请求延时范围(秒)
    'max_retries': 3,           # 最大重试次数
    'timeout': 10,              # 请求超时时间(秒)
    'user_agents': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
}

# ========== 数据字段配置 ==========
DATA_SCHEMA = {
    'required_fields': ['platform', 'title', 'content'],
    'optional_fields': [
        'product_type', 'tags', 'likes', 'comments_count', 'shares',
        'sales', 'price', 'publish_date', 'clean_text', 'sentiment',
        'keywords', 'source_url'
    ]
}

# ========== 可视化配置 ==========
VISUALIZATION_CONFIG = {
    'chinese_fonts': ['SimHei', 'Microsoft YaHei', 'DejaVu Sans'],
    'color_palette': {
        'sentiment': {
            '正面': '#2ECC71',   # 绿色
            '中性': '#95A5A6',   # 灰色  
            '负面': '#E74C3C'    # 红色
        },
        'platforms': {
            '小红书': '#FF2442',
            '抖音': '#000000', 
            '淘宝': '#FF4400'
        }
    },
    'figure_size': (12, 8),
    'dpi': 300
}

# ========== 文件路径模板 ==========
FILE_TEMPLATES = {
    'raw_data': '{platform}_{date}_raw.csv',
    'cleaned_data': '{platform}_{date}_cleaned.csv',
    'analysis_result': 'analysis_{category}_{date}.json',
    'visualization': '{chart_type}_{category}_{date}.png'
}

# ========== 日志配置 ==========
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': PROJECT_ROOT / 'development_doc' / 'project.log'
}

if __name__ == "__main__":
    print("AI硬件分析项目配置")
    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"支持平台: {list(PLATFORMS.keys())}")
    print(f"核心关键词: {SEARCH_KEYWORDS['primary']}") 