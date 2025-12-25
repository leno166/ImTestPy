"""
@文件: ssh.py
@作者: 雷小鸥
@日期: 2025/12/11 16:04
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
# noinspection PyPackageRequirements
import paramiko
import io

from src.terminal import TerminalManager, SshServer
from src.log.logger import logger


class SshConnect:
    def __init__(self, ip: str, port: int = 22, username: str = 'root'):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.ip = ip
        self.port = port
        self.username = username

        logger.info('创建 ssh 连接: %s:%s, 用户: %s', ip, port, username)

    def password_connect(self, password: str):
        self.ssh_client.connect(
            hostname=self.ip,
            port=self.port,
            username=self.username,
            password=password,
            timeout=1
        )

        logger.info('密码连接成功: %s:%s, 用户: %s', self.ip, self.port, self.username)

    def private_key_connect(self, key_info: str, key_type: str, key_fmt: str, passphrase: str = None):
        """
        密钥连接 ssh

        :param key_info: 密钥路径, 密钥字符串内容, 解析好的密钥
        :param key_type: 密钥加密类型, RSA, ECDSA, ED25519
        :param key_fmt: 密钥格式, 文件, 字符串, 解析好的密钥
        :param passphrase: 密钥密码
        :return: 解析好的密钥
        """
        match (key_type, key_fmt):
            case ('RSA', 'FILE'):
                key = paramiko.RSAKey.from_private_key_file(key_info, password=passphrase)
            case ('ECDSA', 'FILE'):
                key = paramiko.ECDSAKey.from_private_key_file(key_info, password=passphrase)
            case ('ED25519', 'FILE'):
                key = paramiko.Ed25519Key.from_private_key_file(key_info, password=passphrase)
            case ('RSA', 'STR'):
                key = paramiko.RSAKey.from_private_key(io.StringIO(key_info), password=passphrase)
            case ('ECDSA', 'STR'):
                key = paramiko.ECDSAKey.from_private_key(io.StringIO(key_info), password=passphrase)
            case ('ED25519', 'STR'):
                key = paramiko.Ed25519Key.from_private_key(io.StringIO(key_info), password=passphrase)
            case ('KEY', 'KEY'):
                key = key_info
            case _:
                raise ValueError(f'Invalid key format: {key_type} and key type: {key_fmt}')

        # noinspection PyUnboundLocalVariable
        self.ssh_client.connect(
            hostname=self.ip,
            port=self.port,
            username=self.username,
            pkey=key,
            timeout=1
        )

        logger.info('密钥连接成功: %s:%s, 用户: %s, 密钥类型: %s, 密钥格式: %s', self.ip, self.port, self.username,
                     key_type, key_fmt)

        return key

    def reconnect(self, method, authentication):
        match method:
            case 'password':
                self.password_connect(authentication)

            case 'key':
                self.private_key_connect(authentication, 'KEY', 'KEY')

            case _:
                raise ValueError(f'无效的认证方式: {method}')


class SshExecutor:
    def __init__(self, ssh_client: paramiko.SSHClient):
        self.ssh_server = SshServer(ssh_client, 'xterm', 1000, 1000)
        self.terminal_manager = TerminalManager(self.ssh_server, self.ssh_server, True)

    def __enter__(self):
        self.terminal_manager.start(True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminal_manager.stop()

    @property
    def input(self):
        raise AttributeError("input is write-only")

    @input.setter
    def input(self, value: str):
        self.terminal_manager.terminal_in.input = value

    def download(self, local_path: str, remote_path: str):
        pass

    def upload(self, local_path: str, remote_path: str):
        pass


