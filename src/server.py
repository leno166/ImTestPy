import threading
import time
from abc import ABC, abstractmethod
from idlelib.iomenu import errors
from typing import NoReturn
import win32pipe
import win32security
import win32file
import uuid
import subprocess
import paramiko


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


ipc = Ipc('terminal')
ipc.create_slave_pipe()

while True:
    print(ipc.read)
    time.sleep(0.1)
