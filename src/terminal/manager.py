"""
@文件: manager.py
@作者: 雷小鸥
@日期: 2025/12/11 16:37
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
import threading
import time

from ..core.ipc import Ipc
from .base import TerminalIn, TerminalOut


class TerminalManager:
    def __init__(self, terminal_in: TerminalIn, terminal_out: TerminalOut, is_script: bool = True):
        self.terminal_in = terminal_in
        self.terminal_out = terminal_out

        self.ipc = Ipc()
        self.pipe_name = self.ipc.pipe_name

        self.running = False
        self.threads: list[threading.Thread] = []

        self.ipc.create_master_pipe()

        if is_script:
            self.terminal_in.input = 'is script'

    def start(self, no_in: bool = False):
        if self.running:
            return

        self.running = True

        thread_func_list = [self.in_loop, self.out_loop, self.err_loop] if not no_in else [self.out_loop, self.err_loop]

        for fn in thread_func_list:
            thread = threading.Thread(target=fn, daemon=True)
            self.threads.append(thread)

        for thread in self.threads:
            thread.start()

    def stop(self):
        self.running = False

        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=1.0)

        self.ipc.close()

    def in_loop(self):
        while self.running:
            print('请输入: ')
            self.terminal_in.input = input()

    def out_loop(self):
        while self.running:
            line = self.terminal_out.out

            if line:
                self.ipc.write('[OUT] ' + line)
            time.sleep(0.01)

    def err_loop(self):
        while self.running:
            line = self.terminal_out.err
            if line:
                self.ipc.write('[ERR] ' + line)
            time.sleep(0.01)

    def user_interaction(self, ipc: Ipc, cmd: str, timeout: float = 20, is_generator: bool = False):
        self.terminal_in.input = f'echo [USER_START]; {cmd}; echo [USER_END]'

        start_time = time.time()
        in_block = False

        def _process_lines():
            nonlocal in_block

            while True:
                if time.time() - start_time > timeout:
                    self.terminal_in.input = '^C'
                    # 清空 IPC buffer
                    ipc.clear()
                    raise TimeoutError(f"Command execution timed out after {timeout} seconds")

                line = ipc.read
                if not line:
                    continue

                if line == '[OUT] [USER_START]':
                    in_block = True
                    continue

                if line == '[OUT] [USER_END]':
                    break

                if in_block:
                    yield line.replace('[OUT]', '').strip()

        try:
            return _process_lines() if is_generator else '\n'.join(_process_lines())

        except TimeoutError:
            return '[TIMEOUT ERROR]' if not is_generator else iter(())

