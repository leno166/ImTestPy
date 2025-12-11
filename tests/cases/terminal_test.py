"""
@文件: terminal_test.py
@作者: 雷小鸥
@日期: 2025/12/11 09:22
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
import pytest
from tests.utils.logger import logger
from tests.utils.terminal import Ipc, TerminalManager, ParamikoSshServer
import time
import threading


@pytest.mark.module
@pytest.mark.ipc
def ipc_test():
    ipc_master = Ipc()
    ipc_master.create_master_pipe()

    ipc_slave = Ipc(ipc_master.pipe_name)
    ipc_slave.create_slave_pipe()

    count = 20

    def master_read_lines():
        for i in range(count):
            ipc_master.write(f'write msg: {i}\n')

        ipc_master.close()

    master_thread = threading.Thread(target=master_read_lines, daemon=True, name='master pipe')
    master_thread.start()

    num = 0
    while num < count:
        line = ipc_slave.read
        num += 1
        logger.info(line)
        assert line.startswith('write msg:')


@pytest.mark.module
@pytest.mark.terminal
def easy_ssh_terminal_test():
    paramiko_ssh_server = ParamikoSshServer('192.168.0.179', 'custom', '654312')

    terminal_manager = TerminalManager(paramiko_ssh_server, paramiko_ssh_server)
    terminal_manager.start(no_in=True)

    ipc = Ipc('terminal')
    ipc.create_slave_pipe()

    paramiko_ssh_server.input = 'tail -f -n +1 /var/log/syslog'

    jump_to_command_line = True
    while jump_to_command_line:
        line = ipc.read
        logger.info(line)
        if 'tail -f -n +1 /var/log/syslog' in line:
            jump_to_command_line = False
            logger.info('\n\n\n')
            logger.info(line)

        time.sleep(0.1)

    logger.info('\n\n\n')

    # change_key_words = True
    # key_line = ''
    # while change_key_words:
    #     line = ipc.read
    #     # logger.info(line)
    #     if 'NetworkManager-dispatcher.service: Succeeded' in line:
    #         logger.info('key line: %s', line)
    #         change_key_words = False
    #         key_line = line
    #
    # paramiko_ssh_server.input = '^C'

    terminal_manager.stop()
