"""
@文件: client.py
@作者: 雷小鸥
@日期: 2025/12/10 10:17
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
# client.py - 管道客户端
import os
import time
import win32pipe
import win32file
import threading


def pipe_client():
    pipe_name = r'\\.\pipe\MyNamedPipe'

    print("尝试连接到管道服务器...")

    while True:
        try:
            # 连接到命名管道
            pipe = win32file.CreateFile(
                pipe_name,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None
            )
            print("已连接到管道服务器")
            break
        except:
            print("等待服务器启动...")
            time.sleep(1)

    while True:
        # 检查键盘输入
        message = input()
        if message:
            win32file.WriteFile((pipe), message.encode('utf-8'))
            print(f"发送: {message}")

        # 接收消息
        try:
            result, data = win32file.ReadFile(pipe, 65536)
            if data:
                print(f"收到: {data}")
        except:
            pass

        time.sleep(0.01)  # 防止CPU占用过高
    # finally:
    #     win32file.CloseHandle(pipe.handle)


if __name__ == "__main__":
    pipe_client()