"""
@文件: ipd.py
@作者: 雷小鸥
@日期: 2025/12/15 09:50
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
from typing import TypedDict, Optional
from paramiko.ssh_exception import AuthenticationException

from .secure_shell import SshConnect, SshExecutor
from .log.logger import logger


class AuthInfo(TypedDict):
    method: str
    ip: str
    port: int
    username: str
    authentication: str


class HostInfo(TypedDict):
    id: int
    project_type: str
    switch_type: str
    connect_type: str
    which_ipd: str
    ip: str
    port: int


# noinspection DuplicatedCode
class KeyLoginInfo(TypedDict):
    id: int
    username: str
    date: str
    private_key: str
    passphrase: str
    key_fmt: str
    key_type: str


class PasswordLoginInfo(TypedDict):
    id: int
    username: str
    password: str


class Ipd:
    def __init__(self):
        pass

    @classmethod
    def auto_connect(
            cls,
            host_infos: list[HostInfo] = None,
            key_login_infos: list[KeyLoginInfo] = None, password_login_infos: list[PasswordLoginInfo] = None,
            auth_info: Optional[AuthInfo] = None
    ):
        logger.info("正在自动连接 ipd 中...")

        if auth_info:
            ssh = SshConnect(auth_info['ip'], auth_info['port'], auth_info['username'])

            try:
                ssh.reconnect(auth_info['method'], auth_info['authentication'])
            except TimeoutError:
                logger.warning(
                    '重连: %s@%s:%s, method: %s, 连接超时. ',
                    auth_info['username'], auth_info['ip'], auth_info['port'], auth_info['method']
                )
                raise ConnectionError('未连接成功')
            except AuthenticationException:
                logger.warning(
                    '重连: %s@%s:%s, method: %s, 连接被拒绝. ',
                    auth_info['username'], auth_info['ip'], auth_info['port'], auth_info['method']
                )
                raise ConnectionError('未连接成功')

            logger.info(
                '重连成功: %s:%s, 用户: %s, 认证方式: %s',
                auth_info['ip'], auth_info['port'], auth_info['username'], auth_info['method']
            )
            return SshExecutor(ssh.ssh_client), auth_info

        if not host_infos:
            raise ConnectionError('未连接成功')

        for host_info in host_infos:
            logger.info(
                '尝试连接: %s, %s, %s, %s',
                host_info['project_type'], host_info['switch_type'],
                host_info['connect_type'], host_info['which_ipd']
            )

            if key_login_infos:
                logger.info('尝试密钥登录...')
                for key_login_info in key_login_infos:
                    ssh = SshConnect(
                        host_info['ip'], host_info['port'], key_login_info['username']
                    )
                    logger.info(
                        '尝试登录: %s@%s:%s',
                        key_login_info['username'], host_info['ip'], host_info['port']
                    )

                    try:
                        key = ssh.private_key_connect(
                            key_login_info['private_key'], key_login_info['key_type'],
                            key_login_info['key_fmt'], key_login_info['passphrase']
                        )
                        auth_info: AuthInfo = {
                            'method': 'key',
                            'ip': host_info['ip'],
                            'port': host_info['port'],
                            'username': key_login_info['username'],
                            'authentication': key,
                        }
                        return SshExecutor(ssh.ssh_client), auth_info
                    except TimeoutError:
                        logger.warning(
                            '密钥登录超时: %s | %s',
                            key_login_info['key_type'], key_login_info['key_fmt']
                        )
                    except AuthenticationException:
                        logger.warning(
                            '密钥被拒绝: %s | %s',
                            key_login_info['key_type'], key_login_info['key_fmt']
                        )

                    auth_info: AuthInfo = {
                        'method': 'key',
                        'ip': host_info['ip'],
                        'port': host_info['port'],
                        'username': key_login_info['username'],
                        'authentication': key,
                    }

                    return SshExecutor(ssh.ssh_client), auth_info

            if password_login_infos:
                logger.info('尝试密码登录...')
                for password_login_info in password_login_infos:
                    logger.info('密码登录, 用户名: %s', password_login_info['username'])
                    ssh = SshConnect(
                        host_info['ip'], host_info['port'], password_login_info['username']
                    )
                    try:
                        ssh.password_connect(password_login_info['password'])
                        auth_info: AuthInfo = {
                            'method': 'password',
                            'ip': host_info['ip'],
                            'port': host_info['port'],
                            'username': password_login_info['username'],
                            'authentication': (password_login_info['password'])
                        }
                        return SshExecutor(ssh.ssh_client), auth_info
                    except TimeoutError:
                        logger.warning('密码登录超时!')
                    except AuthenticationException:
                        logger.warning('密码登录被拒绝')

        raise ConnectionError('未连接成功')
