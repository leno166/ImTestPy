"""
@文件: conftest.py
@作者: 雷小鸥
@日期: 2025/12/9 10:57
@许可: MIT License
@描述: 全局配置文件
@版本: Version 1.0
"""
import pytest


@pytest.fixture()
def restart_ipd_and_test_connection():
    """
    在测试前重启ipd, 并确认ipd已经完成重启.

    :return:
    """
    yield


@pytest.fixture()
def log_collection():
    """
    在测试前和测试后收集日志.

    :return:
    """
    yield log_paths
    # 从 log_paths(列表) 下载日志





