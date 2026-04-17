"""数据库初始化脚本"""

from .database import init_db
from .models import User, Record, CalorieRecord, Collection, PolishRecord


def main():
    """初始化数据库"""
    print("开始初始化数据库...")
    init_db()
    print("数据库初始化完成！")


if __name__ == "__main__":
    main()