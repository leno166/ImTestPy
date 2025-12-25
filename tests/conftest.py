"""
@文件: conftest.py
@作者: 雷小鸥
@日期: 2025/12/9 10:57
@许可: MIT License
@描述: 全局配置文件
@版本: Version 1.0
"""
import pytest
import threading
from src.terminal import TerminalManager, SshServer
from src.core.ipc import Ipc

@pytest.fixture()
def ipc_prepare():
    ipc_master = Ipc()
    ipc_master.create_master_pipe()

    ipc_slave = Ipc(ipc_master.pipe_name)
    ipc_slave.create_slave_pipe()

    def start_master_thread(datas: list[str]):
        def master_write():
            for data in datas:
                ipc_master.write(data)

        master_thread = threading.Thread(target=master_write, daemon=True, name='master write')
        master_thread.start()
        return master_thread

    yield start_master_thread, ipc_slave

@pytest.fixture()
def ssh_terminal_prepare():
    paramiko_ssh_server = SshServer('192.168.0.179', 'custom', '654312')

    terminal_manager = TerminalManager(paramiko_ssh_server, paramiko_ssh_server)
    terminal_manager.start(no_in=True)

    ipc = Ipc(terminal_manager.pipe_name)
    ipc.create_slave_pipe()

    yield terminal_manager, paramiko_ssh_server, ipc



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
    pass
    # yield log_paths
    # 从 log_paths(列表) 下载日志





