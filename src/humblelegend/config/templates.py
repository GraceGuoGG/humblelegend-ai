"""
配置文件模板
"""

SOUL_MD_TEMPLATE = """# HumbleLegend 配置文件

## 用户设置

### 主题列表
topics:
  - name: "饮食作息"
    description: "记录饮食、睡眠、运动等日常健康相关内容"
  - name: "工作"
    description: "记录工作任务、会议、项目进展等"
  - name: "娱乐"
    description: "记录游戏、电影、音乐等娱乐活动"

### 营养目标
nutrition_goal:
  calories: 2000
  protein: 60
  fat: 65
  carbs: 300
  sodium: 2000

### 作息目标
sleep_goal:
  wake_time: "07:00"
  sleep_time: "23:00"

### 饮水目标
water_goal:
  daily_ml: 2000

## 系统设置

### 数据留存周数
data_retention_weeks: 8

### 记忆上限
memory_limit: 1000
"""

ENV_TEMPLATE = """# HumbleLegend 环境变量配置

# 火山引擎API密钥（用于LLM服务）
VOLC_ACCESSKEY=your_access_key_here
VOLC_SECRETKEY=your_secret_key_here

# 数据库路径（可选，默认为 data/database.db）
DATABASE_PATH=data/database.db

# 日志级别（可选，默认为 INFO）
LOG_LEVEL=INFO
"""

REQUIREMENTS_TXT = """# HumbleLegend 依赖

# 核心依赖
pydantic>=2.0.0
loguru>=0.7.0

# LLM服务
volcengine-python-sdk>=1.0.0

# Web框架
fastapi>=0.100.0
uvicorn>=0.23.0

# 数据处理
python-multipart>=0.0.6

# 导出功能
markdown-pdf>=3.0.0

# 开发依赖
pytest>=7.0.0
pytest-asyncio>=0.21.0
"""

README_MD = """# HumbleLegend AI Agent

轻量级AI助手，用于零散信息存档、收集、分析与汇总。

## 功能特性

- **日常记录**：快速记录日常事件，自动识别主题
- **热量估算**：识别食物图片/文本，计算营养成分
- **内容收藏**：收藏文本、图片、视频、链接
- **文本润色**：根据需求润色文本，支持多种风格
- **日报生成**：自动生成今日/历史日报，支持图表
- **主题复盘**：生成主题趋势分析报告

## 快速开始

### 安装

```bash
pip install -r requirements.txt
```

### 配置

1. 复制配置模板：
```bash
cp soul.md.template soul.md
cp .env.template .env
```

2. 编辑 `.env` 文件，填入火山引擎API密钥：
```
VOLC_ACCESSKEY=your_access_key
VOLC_SECRETKEY=your_secret_key
```

### 运行

#### CLI交互模式
```bash
python -m humblelegend
```

#### 单条指令
```bash
python -m humblelegend --input "帮我记录今天完成了项目汇报"
```

#### HTTP API服务
```bash
python -m humblelegend --api --port 8000
```

## 使用示例

### 日常记录
```
帮我记录今天完成了项目汇报
记一下今天吃了两个苹果
```

### 热量估算
```
帮我估算热量，今天吃了一碗米饭
估算一下这个食物的热量 [附图片]
```

### 内容收藏
```
帮我收藏这篇文章 https://example.com/article
收藏这段文字：...
```

### 文本润色
```
帮我润色这段文字：...
正式化润色：...
```

### 日报
```
给我今日日报
给我2024-01-15的日报
```

### 复盘
```
复盘饮食作息
复盘工作
```

## API文档

启动API服务后，访问 `http://localhost:8000/docs` 查看Swagger文档。

### 主要接口

- `POST /process` - 处理用户输入
- `GET /settings` - 获取设置
- `GET /daily-report/today` - 获取今日日报
- `GET /review/{topic}` - 获取主题复盘

## 项目结构

```
humblelegend/
├── agents/           # Agent模块
│   ├── parser.py     # 指令解析
│   ├── record.py     # 记录处理
│   ├── calorie.py    # 热量估算
│   ├── polish.py     # 文本润色
│   ├── collect.py    # 内容收藏
│   ├── daily_report.py # 日报生成
│   ├── review.py     # 复盘分析
│   ├── settings.py   # 设置管理
│   ├── memory.py     # 记忆管理
│   └── orchestrator.py # 主调度
├── core/             # 核心模块
│   ├── config.py     # 配置管理
│   ├── database.py   # 数据库
│   ├── llm.py        # LLM服务
│   └── storage.py    # 文件存储
├── platforms/        # 平台适配
│   ├── cli.py        # CLI
│   ├── wechat.py     # 微信
│   └── feishu.py     # 飞书
├── api/              # HTTP API
│   └── routes.py     # 路由
└── utils/            # 工具函数
    ├── hash.py       # 哈希计算
    ├── time.py       # 时间处理
    └── export.py     # 导出功能
```

## 许可证

MIT License
"""
