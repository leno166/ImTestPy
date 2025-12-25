"""
@文件: __init__.py
@作者: 雷小鸥
@日期: 2025/12/11 16:35
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
from .base import TerminalIn, TerminalOut
from .manager import TerminalManager
from .server import CmdServer, SshServer


def main():
    import time
    from src.core.ipc import Ipc

    cmd_server = CmdServer()
    ssh_server = SshServer('192.168.0.179', 'custom', '654312')

    terminal_manager = TerminalManager(ssh_server, ssh_server)
    terminal_manager.start()

    ipc = Ipc(terminal_manager.pipe_name)
    ipc.create_slave_pipe()

    while True:
        out_line = ipc.read
        if out_line:
            print(out_line.strip())
        time.sleep(0.01)


__all__ = ['TerminalIn', 'TerminalOut', 'TerminalManager', 'CmdServer', 'SshServer', 'main']
