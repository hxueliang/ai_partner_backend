# 公共函数
# 生成会话名
from datetime import datetime


def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
