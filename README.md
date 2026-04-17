# HumbleLegend AI Agent

一款开源可扩展的轻量级AI助手，专注于用户零散信息的存档、收集、分析与汇总，提供日报、复盘两大核心输出能力，支持私有部署、灵活配置及多平台调用。

## 产品定位

HumbleLegend是一款内置多技能、多子Agent的轻量级AI助手，以GitHub开源项目形式呈现，专注于用户零散信息的存档、收集、分析与汇总，提供日报、复盘两大核心输出能力，支持私有部署、灵活配置及多平台调用。

## 核心特性

### 🚀 全流程管理
- 支持用户零散输入的实时存档、分类分析
- 输出按日期的日报及按主题的复盘报告
- 保留近8周的完整数据历史

### 🌐 多端适配
- 人类通过微信、飞书对话框交互
- 其他Agent通过CLI接口实现输入输出传递
- 无GUI界面，轻量化交互体验

### 🔧 开源可扩展
- GitHub开源，支持用户私有部署
- 通过soul.md配置调整功能开关
- 支持二次开发，兼容龙虾系产品调用

### 📊 智能分析
- 内置NLP理解用户输入意图
- 自动识别指令类型及内容分类
- 智能计算热量摄入、营养分析

## 核心功能

### 1. 记录模式 📝
- **日常记录**：帮我记录日常事件、工作内容
- **热量估算**：帮我估算饮食热量、营养成分
- **内容收藏**：帮我收藏文本、图片、视频、链接
- **文本润色**：帮我润色优化文本内容

### 2. 日报模式 📅
- **今日日报**：总结当日核心事件、营养摄入
- **历史日报**：查询近8周内的任意日期
- **数据卡片**：固定核心指标+灵活扩展指标
- **图表展示**：支持柱状图可视化记录数据

### 3. 复盘模式 📈
- **主题复盘**：按主题分析近7天/8周趋势
- **趋势图表**：展示每日记录数量、营养摄入
- **深度分析**：500-800字专业总结报告
- **完整内容**：包含所有相关记录的原始内容

### 4. 设置功能 ⚙️
- **主题管理**：自定义主题分类（最少1个）
- **目标设置**：每日热量、作息、饮水目标
- **数据管理**：手动选择保留/删除历史数据
- **记忆功能**：记录用户操作习惯与偏好

## 快速开始

### 部署选项

#### 1. Render.com（推荐）
```bash
# 一键部署
https://dashboard.render.com/new/web-service?repo=https://github.com/GraceGuoGG/humblelegend-ai
```

#### 2. Docker部署
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

#### 3. 本地启动
```bash
# 安装依赖
pip install -r requirements.txt

# 启动API服务器
python main.py --mode api --host 0.0.0.0 --port 8000

# 或者使用CLI模式
python main.py --mode cli
```

### API接口

```bash
# 健康检查
curl -X GET http://localhost:8000/health

# 处理用户输入
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "input": "帮我记录"}'

# 飞书事件处理
curl -X POST http://localhost:8000/feishu/events \
  -H "Content-Type: application/json" \
  -d '{"event": "message_receive"}'
```

## 配置说明

### soul.md配置

支持通过soul.md调整功能：

```yaml
# soul.md配置示例
features:
  record: true
  daily_report: true
  review: true
  settings: true
  shortcuts: true
  memory: true

default_topics:
  - 饮食作息
  - 工作
  - 娱乐

daily_target:
  calories: 2000
  water: 2000
  sleep:
    start: "22:00"
    end: "07:00"
```

### CLI参数

```bash
# 启动API服务器
python main.py --mode api --host 0.0.0.0 --port 8000

# 直接处理输入
python main.py --mode cli --input "帮我记录"

# 使用JSON输入
python main.py --mode cli --json '{"user_id":"123","input":"帮我记录"}'
```

## 技术架构

### 核心模块

```
humblelegend/
├── src/
│   ├── core/           # 核心应用逻辑
│   │   ├── simple_app.py
│   │   └── simple_database.py
│   ├── platforms/      # 平台适配器
│   │   ├── feishu.py
│   │   ├── cli.py
│   │   └── wechat.py
│   ├── api/            # API接口
│   │   └── simple_server.py
│   ├── humblelegend/   # 主业务模块
│   │   ├── agents/     # 子Agent集合
│   │   ├── core/       # 核心功能
│   │   └── utils/      # 工具函数
│   └── utils/          # 通用工具
│       ├── nutrition_database.py
│       ├── chart_generator.py
│       └── document_exporter.py
└── tests/              # 单元测试
```

### 技术栈

- **Python 3.7+**：核心开发语言
- **FastAPI**：Web框架（可选）
- **SQLite**：本地数据库
- **NLTK/Gensim**：自然语言处理
- **Pillow**：图片处理
- **Matplotlib**：图表生成

## 开发与贡献

### 代码规范

- 遵循PEP8规范
- 使用Google风格文档字符串
- 支持中文与英文注释
- 代码结构清晰，功能模块化

### 开发流程

```bash
# 克隆仓库
git clone https://github.com/GraceGuoGG/humblelegend-ai.git

# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest tests/ -v

# 格式化代码
black src/ tests/
```

### 版本控制

```bash
# 创建分支
git branch feature/new-function

# 提交代码
git add .
git commit -m "Add new function"
git push origin feature/new-function
```

## 部署指南

### 私有部署

#### Windows系统
```powershell
# 启动服务器
python main.py --mode api --host 127.0.0.1 --port 8000
```

#### Linux系统
```bash
# 后台运行
nohup python main.py --mode api --host 0.0.0.0 --port 8000 > server.log 2>&1 &
```

#### MacOS系统
```bash
# 使用brew安装依赖
brew install python3
pip3 install -r requirements.txt
python3 main.py --mode api
```

### 飞书开放平台配置

1. 登录 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 配置事件订阅：
   - 事件类型：`im.message.receive_v1`
   - 请求地址URL：`https://your-domain.com/feishu/events`
4. 配置验证令牌和加密密钥
5. 发布应用

## 故障排查

### 常见问题

1. **端口被占用**
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

2. **依赖安装失败**
   ```bash
   pip install -r requirements.txt --timeout 60
   ```

3. **数据库连接错误**
   - 删除 `humblelegend.db` 重新启动
   - 检查 `data/` 目录权限

4. **飞书回调失败**
   - 检查回调URL是否可公网访问
   - 验证Token和密钥配置

## 许可证

MIT License - 详见 LICENSE 文件

## 联系方式

- **作者**：Grace Guo
- **仓库地址**：https://github.com/GraceGuoGG/humblelegend-ai
- **问题反馈**：https://github.com/GraceGuoGG/humblelegend-ai/issues

## 特别感谢

感谢所有为HumbleLegend项目做出贡献的开发者！

---

*本项目遵循开源精神，欢迎使用、修改和分享！*
