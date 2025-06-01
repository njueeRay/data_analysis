"""
数据验证器 - 用于验证爬取数据的质量和完整性
"""

import re
import pandas as pd
from typing import Dict, List, Any, Tuple
from datetime import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_SCHEMA, PRODUCT_CATEGORIES

class DataValidator:
    """
    数据验证器类
    提供数据质量检查、清洗和验证功能
    """
    
    def __init__(self):
        self.required_fields = DATA_SCHEMA['required_fields']
        self.optional_fields = DATA_SCHEMA['optional_fields']
        self.validation_rules = self._setup_validation_rules()
        
    def _setup_validation_rules(self) -> Dict[str, Any]:
        """设置验证规则"""
        return {
            'title': {
                'min_length': 5,
                'max_length': 200,
                'patterns': [r'[\u4e00-\u9fff]']  # 包含中文
            },
            'content': {
                'min_length': 5,
                'max_length': 1000
            },
            'price': {
                'min_value': 0,
                'max_value': 100000
            },
            'sales': {
                'min_value': 0,
                'max_value': 10000000
            },
            'likes': {
                'min_value': 0,
                'max_value': 10000000
            },
            'comments_count': {
                'min_value': 0,
                'max_value': 100000
            }
        }
    
    def validate_field(self, field_name: str, value: Any) -> Tuple[bool, str]:
        """
        验证单个字段
        
        Args:
            field_name: 字段名
            value: 字段值
            
        Returns:
            (是否有效, 错误信息)
        """
        if field_name not in self.validation_rules:
            return True, ""
            
        rules = self.validation_rules[field_name]
        
        # 检查字符串长度
        if isinstance(value, str):
            if 'min_length' in rules and len(value) < rules['min_length']:
                return False, f"{field_name}长度不足{rules['min_length']}字符"
            if 'max_length' in rules and len(value) > rules['max_length']:
                return False, f"{field_name}长度超过{rules['max_length']}字符"
            
            # 检查正则模式
            if 'patterns' in rules:
                for pattern in rules['patterns']:
                    if not re.search(pattern, value):
                        return False, f"{field_name}不符合格式要求"
        
        # 检查数值范围
        if isinstance(value, (int, float)) and value is not None:
            if 'min_value' in rules and value < rules['min_value']:
                return False, f"{field_name}小于最小值{rules['min_value']}"
            if 'max_value' in rules and value > rules['max_value']:
                return False, f"{field_name}大于最大值{rules['max_value']}"
        
        return True, ""
    
    def validate_item(self, item: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证单条数据
        
        Args:
            item: 数据项
            
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        # 检查必需字段
        for field in self.required_fields:
            if field not in item or item[field] is None or item[field] == "":
                errors.append(f"缺失必需字段: {field}")
                continue
                
            # 验证字段值
            is_valid, error_msg = self.validate_field(field, item[field])
            if not is_valid:
                errors.append(error_msg)
        
        # 检查可选字段
        for field in self.optional_fields:
            if field in item and item[field] is not None:
                is_valid, error_msg = self.validate_field(field, item[field])
                if not is_valid:
                    errors.append(error_msg)
        
        return len(errors) == 0, errors
    
    def clean_text(self, text: str) -> str:
        """
        清理文本内容
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not isinstance(text, str):
            return str(text) if text is not None else ""
        
        # 去除多余空格和换行
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 去除特殊字符但保留中文、英文、数字和基本标点
        text = re.sub(r'[^\u4e00-\u9fff\u0030-\u0039\u0041-\u005a\u0061-\u007a\uff01-\uff5e\u3000-\u303f\s]', '', text)
        
        return text
    
    def clean_price(self, price: Any) -> float:
        """
        清理价格数据
        
        Args:
            price: 原始价格
            
        Returns:
            清理后的价格
        """
        if price is None:
            return 0.0
            
        if isinstance(price, (int, float)):
            return float(price)
        
        if isinstance(price, str):
            # 提取数字
            price_match = re.search(r'[\d,]+\.?\d*', price.replace(',', ''))
            if price_match:
                try:
                    return float(price_match.group())
                except ValueError:
                    return 0.0
        
        return 0.0
    
    def clean_count(self, count: Any) -> int:
        """
        清理计数类数据（销量、点赞数等）
        
        Args:
            count: 原始计数
            
        Returns:
            清理后的计数
        """
        if count is None:
            return 0
            
        if isinstance(count, int):
            return count
        
        if isinstance(count, float):
            return int(count)
        
        if isinstance(count, str):
            # 处理中文数字单位
            count = count.replace('万', '0000').replace('千', '000').replace('k', '000').replace('K', '000')
            count = count.replace('+', '').replace('人付款', '').replace('人', '')
            
            # 提取数字
            count_match = re.search(r'\d+', count)
            if count_match:
                try:
                    return int(count_match.group())
                except ValueError:
                    return 0
        
        return 0
    
    def clean_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理单条数据
        
        Args:
            item: 原始数据项
            
        Returns:
            清理后的数据项
        """
        cleaned_item = item.copy()
        
        # 清理文本字段
        text_fields = ['title', 'content', 'shop_name', 'location']
        for field in text_fields:
            if field in cleaned_item:
                cleaned_item[field] = self.clean_text(cleaned_item[field])
        
        # 清理价格
        if 'price' in cleaned_item:
            cleaned_item['price'] = self.clean_price(cleaned_item['price'])
        
        # 清理计数字段
        count_fields = ['sales', 'likes', 'comments_count', 'shares']
        for field in count_fields:
            if field in cleaned_item:
                cleaned_item[field] = self.clean_count(cleaned_item[field])
        
        # 确保product_type有效
        if 'product_type' in cleaned_item:
            if cleaned_item['product_type'] not in PRODUCT_CATEGORIES:
                cleaned_item['product_type'] = "其他AI产品"
        
        # 清理标签
        if 'tags' in cleaned_item and isinstance(cleaned_item['tags'], list):
            cleaned_item['tags'] = [self.clean_text(tag) for tag in cleaned_item['tags'] if tag]
        
        return cleaned_item
    
    def validate_dataset(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        验证整个数据集
        
        Args:
            data_list: 数据列表
            
        Returns:
            验证报告
        """
        if not data_list:
            return {
                "总数": 0,
                "有效数": 0,
                "无效数": 0,
                "有效率": "0%",
                "错误统计": {},
                "清理前后对比": {}
            }
        
        valid_count = 0
        invalid_count = 0
        error_stats = {}
        
        for item in data_list:
            is_valid, errors = self.validate_item(item)
            
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
                
                # 统计错误类型
                for error in errors:
                    error_type = error.split(':')[0] if ':' in error else error
                    error_stats[error_type] = error_stats.get(error_type, 0) + 1
        
        report = {
            "总数": len(data_list),
            "有效数": valid_count,
            "无效数": invalid_count,
            "有效率": f"{valid_count/len(data_list)*100:.1f}%",
            "错误统计": error_stats,
            "字段完整性": self._analyze_field_completeness(data_list)
        }
        
        return report
    
    def _analyze_field_completeness(self, data_list: List[Dict[str, Any]]) -> Dict[str, str]:
        """分析字段完整性"""
        if not data_list:
            return {}
        
        field_stats = {}
        total_count = len(data_list)
        
        all_fields = self.required_fields + self.optional_fields
        
        for field in all_fields:
            non_empty_count = sum(
                1 for item in data_list 
                if field in item and item[field] is not None and item[field] != ""
            )
            completion_rate = non_empty_count / total_count * 100
            field_stats[field] = f"{completion_rate:.1f}%"
        
        return field_stats
    
    def clean_dataset(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        清理整个数据集
        
        Args:
            data_list: 原始数据列表
            
        Returns:
            清理后的数据列表
        """
        cleaned_data = []
        
        for item in data_list:
            cleaned_item = self.clean_item(item)
            
            # 再次验证清理后的数据
            is_valid, _ = self.validate_item(cleaned_item)
            if is_valid:
                cleaned_data.append(cleaned_item)
        
        return cleaned_data

def main():
    """测试数据验证器"""
    validator = DataValidator()
    
    # 测试数据
    test_data = [
        {
            'platform': '淘宝',
            'title': 'AI智能音箱测试商品',
            'content': '这是一个测试商品描述',
            'price': 299.99,
            'sales': 1000
        },
        {
            'platform': '淘宝',
            'title': '',  # 无效：标题为空
            'content': '另一个测试商品',
            'price': -10  # 无效：价格为负
        }
    ]
    
    # 验证数据集
    report = validator.validate_dataset(test_data)
    print("验证报告:")
    for key, value in report.items():
        print(f"{key}: {value}")
    
    # 清理数据集
    cleaned_data = validator.clean_dataset(test_data)
    print(f"\n清理后有效数据: {len(cleaned_data)} 条")

if __name__ == "__main__":
    main() 