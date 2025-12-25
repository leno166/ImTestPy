"""
@文件: 刷包.py
@作者: 雷小鸥
@日期: 2025/12/22 14:53
@许可: MIT License
@描述:
    刷入可修改 VIN VSN 的 MCU 软件包
@版本: Version 1.0
"""
from ..ipd import Ipd

ipd = Ipd()

ipd.auto_connect()
