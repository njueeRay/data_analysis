# AI硬件分析项目

## 🎯 项目目标

通过整合**小红书、抖音、淘宝**等平台的公开数据，分析当前市场上**AI陪伴类硬件（尤其是带二次元属性的产品）**的：

- 产品类型与热点趋势
- 用户反馈（情感、偏好、痛点）
- 市场活跃度（互动量、发布时间段）
- 潜在用户画像（偏好特征）

最终构建一份有数据支持的**宏观市场视角**，提供可视化图表和数据报告。

## 📁 项目结构

```
ai_hardware_analysis_project/
├── .cursor/                    # Cursor规则指导集
├── guidance/                   # 项目指导文档
├── development_doc/            # 开发文档和日志
├── crawler/                    # 爬虫模块
├── data_processing/            # 数据处理模块  
├── analysis/                   # 分析模块
├── visualization/              # 可视化模块
├── raw_data/                   # 原始数据
├── cleaned_data/               # 清洗数据
├── visualizations_output/      # 图表输出
├── report/                     # 分析报告
├── config.py                   # 项目配置
├── requirements.txt            # 依赖列表
└── README.md                   # 项目说明
```

## 🚀 快速开始

### 1. 环境搭建

```bash
# 安装依赖
pip install -r requirements.txt

# 验证配置
python config.py
```

### 2. 数据采集

```bash
# 运行爬虫（按优先级）
python crawler/taobao_crawler.py
python crawler/xiaohongshu_crawler.py  
python crawler/douyin_crawler.py
```

### 3. 数据处理

```bash
# 数据清洗和预处理
python data_processing/data_cleaner.py
python data_processing/text_processor.py
```

### 4. 数据分析

```bash
# 运行分析模块
python analysis/product_analysis.py
python analysis/user_analysis.py
python analysis/platform_comparison.py
```

### 5. 可视化生成

```bash
# 生成图表
python visualization/chart_generator.py
```

## 📊 分析维度

### 1. 产品维度分析
- 产品类别分布（AI音箱、陪伴机器人、虚拟伴侣等）
- 价格区间分布
- 上市时间趋势

### 2. 用户偏好与反馈分析  
- 高频关键词提取
- 情绪倾向分析（正面/中性/负面）
- 用户画像构建

### 3. 内容传播与互动热度分析
- 互动量分布（点赞、评论、转发）
- 发布时间与热度关系

### 4. 平台对比分析
- 平台特性差异
- 关键词差异性分析

### 5. 竞品聚焦分析
- 单产品深度分析
- 热门产品对比

## 🛠️ 技术栈

- **数据采集**: Selenium, Playwright, requests
- **数据处理**: pandas, numpy
- **中文NLP**: jieba, SnowNLP, wordcloud
- **可视化**: matplotlib, seaborn, plotly, pyecharts
- **存储**: CSV, JSON

## 📋 数据字段说明

| 字段名 | 类型 | 说明 |
|-------|------|------|
| platform | string | 数据来源平台 |
| product_type | string | 产品分类 |
| title | string | 内容标题 |
| content | string | 正文或评论 |
| likes | int | 点赞数量 |
| comments_count | int | 评论数 |
| sentiment | string | 情绪分类 |
| keywords | list | 关键词列表 |

完整字段说明见：[数据字段模板](guidance/数据字段模板.md)

## 📈 输出成果

- **原始数据**: 三大平台的结构化数据文件
- **分析报告**: 详细的市场分析报告
- **可视化图表**: 
  - 产品类型分布图
  - 用户情绪分析图
  - 关键词词云图
  - 平台对比雷达图
  - 热度趋势时间图

## 📚 文档指引

- [任务需求详情](guidance/任务需求.md)
- [Cursor规则指导集](.cursor/main-guide.mdc)
- [爬虫策略](guidance/爬虫策略.md)  
- [数据处理方案](guidance/数据处理与分析方案.md)
- [图表分析清单](guidance/图表分析_示例清单.md)

## ⚡ 注意事项

- 所有文本处理必须考虑中文特性
- 爬虫开发注意反爬策略和延时控制
- 可视化图表必须支持中文字体
- 数据字段严格按照模板标准化

## 📝 开发日志

开发进度和详细日志记录在 `development_doc/` 目录下。

---

**项目状态**: 🚀 开发中  
**最后更新**: 2025-01-01 