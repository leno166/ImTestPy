"""
@文件: logger.py
@作者: 雷小鸥
@日期: 2025/12/9 11:09
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
import logging
import re
from pathlib import Path
from datetime import datetime, timedelta
from src.core.configuration import CONFIGURATION

WORKING_PATH = Path(__file__).parent.parent.parent

LOG_PATH = CONFIGURATION['LOGGING']['path']
LOG_DIR_PATH = WORKING_PATH / LOG_PATH
LOG_DIR_PATH.mkdir(exist_ok=True)

LOG_NAME = CONFIGURATION['LOGGING']['name']

LOG_TIMESTAMP_STR = CONFIGURATION['LOGGING']['timestamp_fmt']
LOG_TIMESTAMP = datetime.now().strftime(LOG_TIMESTAMP_STR)

LOG_FILE_PATH = LOG_DIR_PATH / f'{LOG_NAME} {LOG_TIMESTAMP}.log'

logger = logging.getLogger(LOG_NAME)


def is_old(path, days=30):
    match = re.search(rf'{re.escape(LOG_NAME)} (\d{{4}}年\d{{2}}月\d{{2}}日)', path.name)
    if not match:
        return False
    file_date_str = match.group(1)
    file_date = datetime.strftime(file_date_str, "%Y年%m月%d日").date()
    cutoff_date = datetime.now().date() - timedelta(days=days)
    return file_date < cutoff_date


def cleanup_old_logs(days):
    for log in LOG_DIR_PATH.glob(f'{LOG_NAME} *.log'):
        if is_old(log, days=days):
            log.unlink()
            logger.info('deleted old log file: %s', log)


def setup_logger():
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    #   占位符             含义
    # %(filename)s      源文件名（不含路径），如 main.py
    # %(pathname)s      完整文件路径
    # %(lineno)d        日志调用所在的行号
    # %(funcName)s      调用日志的函数名
    # %(module)s        模块名（通常是文件名不含 .py）
    # %(name)s          logger 的名字（你这里是 'system'）
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-1s | %(filename)s:%(lineno)4d - %(funcName)s() ->| %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # file handler - record to system logs
    file_handler = logging.FileHandler(LOG_FILE_PATH, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # console handler - record to controller logs
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)

    # add handler to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # 清理旧日志（可选：只在首次 setup 时清理一次）
    cleanup_old_logs(days=30)

    logger.info(f"Logger initialized. Writing to: {LOG_FILE_PATH}")
    return logger


setup_logger()
