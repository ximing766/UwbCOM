from rich.logging import RichHandler
import logging
from logging.handlers import RotatingFileHandler
import os

# 创建日志目录
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 日志格式
log_format = "[%(asctime)s.%(msecs)03d] | %(levelname)-7s | %(message)s"

# 基础配置
logging.basicConfig(
    level=logging.INFO,  # 设置更合理的日志级别
    format=log_format,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        RichHandler(rich_tracebacks=True),  # 启用异常追踪
        RotatingFileHandler(  # 使用轮转日志
            os.path.join(log_dir, 'app.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
    ]
)

# 获取logger
log = logging.getLogger("rich")

# 测试日志
log.info("这是一条信息日志")
log.warning("这是一条警告日志")
log.info("这是一条信息日志")
log.error("这是一条错误日志")
log.info("这是一条信息日志")