"""
简化测试脚本 - 验证基础组件
"""

print("开始简化测试...")

# 测试1：配置文件
try:
    from config import PLATFORMS, SEARCH_KEYWORDS
    print("✅ 配置文件正常")
    print(f"平台数量: {len(PLATFORMS)}")
    print(f"关键词数量: {len(SEARCH_KEYWORDS['primary'])}")
except Exception as e:
    print(f"❌ 配置文件错误: {e}")

# 测试2：模块导入
try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    print("✅ 路径配置正常")
except Exception as e:
    print(f"❌ 路径配置错误: {e}")

print("测试完成") 