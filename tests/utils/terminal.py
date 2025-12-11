"""
@文件: terminal.py
@作者: 雷小鸥
@日期: 2025/12/10 10:54
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
import threading
import time
from abc import ABC, abstractmethod
from typing import NoReturn
import win32pipe
import win32security
import win32file
import uuid
import subprocess
import paramiko
from tests.utils.logger import logger


class Ipc:
    ENCODING = 'utf-8'
    BUFFER_SIZE = 65536
    TIMEOUT = 0

    def __init__(self, pipe_name=None):
        self.pipe_name: str = pipe_name or uuid.uuid4().hex
        if not self.pipe_name.startswith(r'\\.'):
            self.pipe_name = r'\\.\pipe\ipc_pipe_' + self.pipe_name

        self.sa = win32security.SECURITY_ATTRIBUTES()  # 创建默认安全属性
        self.sa.bInheritHandle = True  # 可选：是否可继承

        self.pipe = None
        self.pipe_mode = ''

        self.lock = threading.Lock()
        self.r_lock = threading.RLock()

    def create_master_pipe(self):
        self.pipe = win32pipe.CreateNamedPipe(
            self.pipe_name,
            win32pipe.PIPE_ACCESS_DUPLEX,  # 双向通信（可读可写）
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
            win32pipe.PIPE_UNLIMITED_INSTANCES,
            self.BUFFER_SIZE,  # 输出缓冲区大小
            self.BUFFER_SIZE,  # 输入缓冲区大小
            self.TIMEOUT,  # 默认超时时间
            self.sa  # 默认安全属性
        )
        self.pipe_mode = 'master'

    def create_slave_pipe(self):
        self.pipe = (win32file.CreateFile(
            self.pipe_name,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,  # 读 / 写 权限
            0,
            None,
            win32file.OPEN_EXISTING,  # 关键！ 表示只打开已存在的文件/管道，不会创建新管道
            0,
            None
        ))
        self.pipe_mode = 'slave'

    def write(self, msg: str):
        if not self.pipe:
            raise AttributeError("Pipe not initialized. Call create_master_pipe() or create_slave_pipe() first.")

        if self.pipe_mode == 'master':
            win32pipe.ConnectNamedPipe(self.pipe, None)

        with self.lock:
            win32file.WriteFile(self.pipe, msg.encode(self.ENCODING))

    @property
    def read(self):
        if not self.pipe:
            raise AttributeError("Pipe not initialized. Call create_master_pipe() or create_slave_pipe() first.")

        if self.pipe_mode == 'master':
            win32pipe.ConnectNamedPipe(self.pipe, None)

        with self.r_lock:
            result, data = win32file.ReadFile(self.pipe, self.BUFFER_SIZE)

        if data:
            return data.decode(self.ENCODING)

        raise IOError('未读取到数据: %s, %s', result, data)

    def close(self):
        if self.pipe:
            win32file.CloseHandle(self.pipe)
            self.pipe = None


class TerminalIn(ABC):
    """
    命令输入处理抽象基类，定义输入接口规范。

    子类必须实现 input 属性的读写方法，
    其中读取操作应抛出错误（因为该属性设计为只写）。
    """

    @property
    @abstractmethod
    def input(self) -> NoReturn:
        """
        获取输入内容（设计为只写属性，直接访问会抛出错误）

        :raises AttributeError: 当尝试读取该属性时抛出
        """
        raise AttributeError('input 属性是只写的，不能读取')

    @input.setter
    @abstractmethod
    def input(self, value: str) -> NoReturn:
        """
        设置输入内容

        :param value: 要输入的字符串内容
        """
        pass


class TerminalOut(ABC):
    """
    命令输出处理抽象基类，定义输出接口规范。

    子类必须实现 out 和 err 两个只读属性，
    分别用于获取标准输出和错误输出。
    """

    @property
    @abstractmethod
    def out(self) -> str:
        """
        获取标准输出内容

        :return: 标准输出的字符串内容
        """
        return ''

    @property
    @abstractmethod
    def err(self) -> str:
        """
        获取错误输出内容

        :return: 错误输出的字符串内容
        """
        return ''


class TerminalManager:
    def __init__(self, terminal_in: TerminalIn, terminal_out: TerminalOut):
        self.terminal_in = terminal_in
        self.terminal_out = terminal_out

        self.ipc = Ipc('terminal')

        self.running = False
        self.threads: list[threading.Thread] = []

        self.ipc.create_master_pipe()

    def start(self):
        if self.running:
            return

        self.running = True

        thread_in = threading.Thread(target=self.in_loop, daemon=True, name="InputThread")
        thread_out = threading.Thread(target=self.out_loop, daemon=True, name="OutputThread")
        thread_err = threading.Thread(target=self.err_loop, daemon=True, name="ErrorThread")

        self.threads: list[threading.Thread] = [thread_in, thread_out, thread_err]

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


class CmdServer(TerminalIn, TerminalOut):
    def __init__(self):
        self.process = subprocess.Popen(
            ["cmd.exe"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )

    @property
    def input(self) -> NoReturn:
        return super().input

    @input.setter
    def input(self, value):
        if not value.endswith('\n'):
            value += '\n'
        self.process.stdin.write(value.encode('gbk'))
        self.process.stdin.flush()

    @property
    def out(self) -> str:
        return self.process.stdout.readline().decode('gbk')

    @property
    def err(self) -> str:
        return self.process.stderr.readline().decode('gbk')


class ParamikoSshServer(TerminalIn, TerminalOut):
    def __init__(self, hostname: str, username: str, password: str):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.client.connect(
            hostname=hostname, username=username, password=password
        )

        self.channel = self.client.invoke_shell(term='xterm', width=1000, height=1000)

        self.out_buffer = b''
        self.err_buffer = ''

    @property
    def input(self) -> NoReturn:
        return super().input

    @input.setter
    def input(self, value):
        if not self.channel:
            raise ConnectionError("SSH连接已关闭")

        if not value.endswith('\n'):
            value += '\n'

        self.channel.send(value.encode('utf-8'))

    def extract_line_from_buffer(self, buffer: str):
        new_line_pos = buffer.find('\n')
        line = buffer[:new_line_pos]
        remaining = buffer[new_line_pos + 1:]
        return line, remaining

    def read_available_lines(self):
        if self.channel.recv_ready():
            self.out_buffer += self.channel.recv(4096)

    @property
    def out(self) -> str:
        if self.out_buffer and b'\n' in self.out_buffer:
            self.out_buffer = self.out_buffer

            self.out_buffer = self.out_buffer.split(b'\n')
            line = self.out_buffer[0].decode('utf-8', errors='ignore')
            self.out_buffer = self.out_buffer[1:]
            self.out_buffer = b'\n'.join(self.out_buffer)
            return line

        self.read_available_lines()

    @property
    def err(self) -> str:
        if self.err_buffer:
            line, self.err_buffer = self.extract_line_from_buffer(self.err_buffer)
            if line:
                return line

        if self.channel.recv_stderr_ready():
            data = self.channel.recv_stderr(4096)
            if data:
                self.err_buffer += data.decode('utf-8', errors='ignore')
                line, self.err_buffer = self.extract_line_from_buffer(self.err_buffer)
                return line

        return ''


if __name__ == '__main__':
    # cmd_server = CmdServer()
    paramiko_ssh_server = ParamikoSshServer('192.168.0.179', 'custom', '654312')

    terminal_manager = TerminalManager(paramiko_ssh_server, paramiko_ssh_server)
    terminal_manager.start()

    # time.sleep(100)

    ipc = Ipc('terminal')
    ipc.create_slave_pipe()

    while True:
        print(ipc.read)
        time.sleep(0.01)
