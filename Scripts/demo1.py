"""
@文件: demo1.py
@作者: 雷小鸥
@日期: 2025/12/23 14:22
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
from src.ipd import Ipd, HostInfo, KeyLoginInfo, PasswordLoginInfo
from src.core.ipc import Ipc
import time


def main():
    ipd = Ipd()

    host_info: HostInfo = {
        'id': 0,
        'project_type': 'c_suv',
        'switch_type': '100',
        'connect_type': 'obd',
        'which_ipd': 'r_ipd',
        'ip': '172.31.7.13',
        'port': 22,
    }

    password_login_info: PasswordLoginInfo = {
        'id': 0,
        'username': 'root',
        'password': 'root',
    }

    ssh, auth = ipd.auto_connect(
        host_infos=[host_info], password_login_infos=[password_login_info]
    )

    with ssh:
        ipc = Ipc()
        ipc.pipe_name = ssh.terminal_manager.pipe_name
        ipc.create_slave_pipe()

        receive = ssh.terminal_manager.user_interaction(ipc, 'ps -A | grep -i "tn"')
        print('TN 进程:')
        print(receive.strip())

        ipc.close()
        ssh.terminal_manager.terminal_in.input = 'tail -f /opt/m0/logs/camera_s*'
        now = time.time()
        empty_num = 0
        while True:
            if time.time() - now > 5:
                ssh.terminal_manager.terminal_in.input = '^C'
                ipc.clear()
                break

            line = ipc.read
            if not line:
                empty_num += 1

            time.sleep(1)

        now = time.time()
        while time.time() - now < 180:
            ssh.terminal_manager.user_interaction(ipc, 'cd /opt/m0/corefile')
            receive = ssh.terminal_manager.user_interaction(ipc, 'ls -l | grep ^d | grep dumper')
            if receive.strip() != '':
                print(f'core file 下 --> {receive.strip()}')

            ssh.terminal_manager.user_interaction(ipc, 'cd /opt/m0/corefile/coredump')
            receive = ssh.terminal_manager.user_interaction(ipc, 'ls -l | grep ^d')
            if receive.strip() != '':
                print(f'core dump 下 --> {receive.strip()}')

            time.sleep(10)

        print('准备下一组. ')
        receive = ssh.terminal_manager.user_interaction(ipc, 'common_if_testapp -mcureset')

        ipc.close()

        time.sleep(30)


if __name__ == '__main__':
    num = 0
    while True:
        num += 1

        print(f'...第{num}次测试...')
        main()
