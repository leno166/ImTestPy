"""
@文件: configuration.py
@作者: 雷小鸥
@日期: 2025/12/9 13:17
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
from typing import TypedDict
from pathlib import Path
import configparser


class EmailConfig(TypedDict):
    smtp_server: str
    sender: str
    sender_name: str
    authorization: str

    receiver: str
    receiver_name: str

    encoding: str


class LoggingConfig(TypedDict):
    name: str
    path: str
    timestamp_fmt: str


class ConfigurationDict(TypedDict):
    EMAIL: EmailConfig
    LOGGING: LoggingConfig


# todo: 修改成相对路径
TEST_PATH = Path(r'D:\workflow\ImTestPy\tests')

CONF = configparser.ConfigParser(interpolation=None)
CONF.read(TEST_PATH / 'configs' / 'config.ini')

# 提供只读配置
CONFIGURATION: ConfigurationDict = {k: dict(v) for k, v in CONF.items() if k != 'DEFAULT'}  # type: ignore
