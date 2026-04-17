# 使用Python 3.9作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV DATABASE_URL=sqlite:///./humblelegend.db
ENV LOG_LEVEL=INFO

# 初始化数据库
RUN python -c "from src.core import init_db; init_db()"

# 启动命令
CMD ["python", "main.py", "--mode", "api"]