"""
@文件: ipd_test.py
@作者: 雷小鸥
@日期: 2025/12/15 10:30
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
from src.ipd import Ipd, HostInfo, KeyLoginInfo, PasswordLoginInfo
from src.core.ipc import Ipc


# 1. ipd ssh obd 060 password connect test
# 2. ipd ssh obd 060 key connect test
# 3. ipd ssh rj45 060 password connect test
#


def ipd_test():
    ipd = Ipd()

    host_info: HostInfo = {
        'id': 0,
        'project_type': 'linux_pc',
        'switch_type': 'Normal',
        'connect_type': 'Normal',
        'which_ipd': 'False',
        'ip': 'localhost',
        'port': 2222,
    }

    password_login_info: PasswordLoginInfo = {
        'id': 0,
        'username': 'test',
        'password': '654312',
    }

    ssh, auth = ipd.auto_connect(
        host_infos=[host_info], password_login_infos=[password_login_info]
    )

    with ssh:
        ipc = Ipc()
        ipc.pipe_name = ssh.terminal_manager.pipe_name
        ipc.create_slave_pipe()

        receive = ssh.terminal_manager.user_interaction(ipc, 'ls')
        print(receive)

        receive = ssh.terminal_manager.user_interaction(ipc, 'cd /')
        print(receive)

        receive = ssh.terminal_manager.user_interaction(ipc, 'pwd')
        print(receive)

        ipc.close()


if __name__ == '__main__':
    ipd_test()
