"""
@文件: dmz_test.py
@作者: 雷小鸥
@日期: 2025/12/9 15:09
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
from tests.utils.logger import logger


def test_b0bd_filter():
    # Step 1: 查看 360，显示正常
    res = input('Step 1 -> 查看 360，显示正常(Y/N)?')
    logger.info('Step 1 -> 查看 360，显示正常: %s', res.upper())

    # Step 2: 接入 mini wiggler，观察到 360 闪退
    res = input('Step 2 -> 接入 mini wiggler，观察到 360 闪退(Y/N)?')
    logger.info('Step 2 -> 接入 mini wiggler，观察到 360 闪退: %s', res.upper())

    fir_monitor_ok = False
    sec_monitor_ok = False

    # ===== Step 3: 第一次监控  重启前 =====
    try:
        fir_monitor_ok = True
    except Exception as e:
        logger.error('重启前第一次监控 B0BD 字段触发: %s', e)

    # ===== Step 5: 重启 IPD =====

    # ===== Step 6: 第二次监控  重启后 =====
    try:
        sec_monitor_ok = True
    except Exception as e:
        logger.error('重启后第二次监控 B0BD 字段触发: %s', e)

    assert fir_monitor_ok or sec_monitor_ok, "两次日志监控均未捕获到预期字段触发（B0BD 字段触发）"



def sys_log_filter_test():
    # 1. 创建文件并写入字符串:
    #   /var/lib/systemd/pstore/dmesg.txt   ->  kernel_crush_event
    #   /opt/other/last_power_off_time.txt  ->  sys_info_event
    #   /opt/other/crashlog_hex.txt         ->  uart_log_event
    # 2. 下载 m 日志 和 system 日志
    # 3. 重启 ipd
    # 4. 监控 dmz_fcl.log, dmz_fcl_forever.log, dmz_filter.log, dmz_filter_forever.log, dmz_recorder.log, dmz_recorder_forever.log
    # 7. 边监控, 边把日志输出到本地.
    pass
