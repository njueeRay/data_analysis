"""
爬虫模块测试脚本
用于验证爬虫基础组件的功能
"""

import sys
from datetime import datetime

def test_config():
    """测试配置文件"""
    print("=== 测试配置文件 ===")
    try:
        from config import PLATFORMS, SEARCH_KEYWORDS, PRODUCT_CATEGORIES
        print("✅ 配置文件导入成功")
        print(f"支持平台: {list(PLATFORMS.keys())}")
        print(f"主要关键词数量: {len(SEARCH_KEYWORDS['primary'])}")
        print(f"产品分类数量: {len(PRODUCT_CATEGORIES)}")
        return True
    except Exception as e:
        print(f"❌ 配置文件测试失败: {e}")
        return False

def test_data_validator():
    """测试数据验证器"""
    print("\n=== 测试数据验证器 ===")
    try:
        from crawler.data_validator import DataValidator
        
        validator = DataValidator()
        print("✅ 数据验证器创建成功")
        
        # 测试数据
        test_data = [
            {
                'platform': '淘宝',
                'title': 'AI智能音箱测试商品',
                'content': '这是一个测试商品描述，包含智能语音功能',
                'price': 299.99,
                'sales': 1000
            }
        ]
        
        # 验证数据
        report = validator.validate_dataset(test_data)
        print(f"✅ 数据验证完成，有效率: {report['有效率']}")
        
        # 清理数据
        cleaned_data = validator.clean_dataset(test_data)
        print(f"✅ 数据清理完成，处理 {len(cleaned_data)} 条数据")
        
        return True
    except Exception as e:
        print(f"❌ 数据验证器测试失败: {e}")
        return False

def test_base_crawler():
    """测试基础爬虫类"""
    print("\n=== 测试基础爬虫类 ===")
    try:
        from crawler.base_crawler import BaseCrawler
        print("✅ 基础爬虫类导入成功")
        
        # 注意：BaseCrawler是抽象类，不能直接实例化
        # 只测试导入是否成功
        return True
    except Exception as e:
        print(f"❌ 基础爬虫类测试失败: {e}")
        return False

def test_taobao_crawler():
    """测试淘宝爬虫类"""
    print("\n=== 测试淘宝爬虫类 ===")
    try:
        from crawler.taobao_crawler import TaobaoCrawler
        
        crawler = TaobaoCrawler()
        print("✅ 淘宝爬虫创建成功")
        
        # 测试URL构建
        test_url = crawler.build_search_url("AI音箱", 1)
        print(f"✅ URL构建测试: {test_url[:50]}...")
        
        # 测试价格提取
        test_price = crawler.extract_price("￥299.99")
        print(f"✅ 价格提取测试: {test_price}")
        
        # 测试销量提取
        test_sales = crawler.extract_sales("1000+人付款")
        print(f"✅ 销量提取测试: {test_sales}")
        
        # 测试产品分类
        test_category = crawler.classify_product("小米AI智能音箱")
        print(f"✅ 产品分类测试: {test_category}")
        
        return True
    except Exception as e:
        print(f"❌ 淘宝爬虫测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print(f"开始测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    # 运行所有测试
    tests = [
        test_config,
        test_data_validator, 
        test_base_crawler,
        test_taobao_crawler
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ 测试 {test_func.__name__} 异常: {e}")
    
    print("="*50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！爬虫模块基础组件正常")
    else:
        print("⚠️  部分测试失败，需要检查相关组件")
    
    print(f"测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 