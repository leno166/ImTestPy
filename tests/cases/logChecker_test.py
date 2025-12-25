"""
@文件: logChecker_test.py
@作者: 雷小鸥
@日期: 2025/12/9 17:08
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
import pytest

from src.log.logChecker import DmzFclParser, DmzFilterParser, DmzRecorderParser


@pytest.mark.api
def DmzFclParser_test():
    dmz_fcl_parser = DmzFclParser()
    with open(r'D:\workflow\ImTestPy\tests\data\dmz_log_temp\dmz_fcl.log.2025-12-08_17_20_29.072327602', 'r',
              encoding='utf-8') as f:
        for l in dmz_fcl_parser.read(f):
            assert len(l.level) == 3
            assert l.run_time is not None
            assert l.timestamp is not None
            assert l.msg is not None


@pytest.mark.api
def DmzFilterParser_test():
    dmz_filter_parser = DmzFilterParser()
    with open(r'D:\workflow\ImTestPy\tests\data\dmz_log_temp\dmz_filter.log.2025-12-08_17_20_29.305614398', 'r',
              encoding='utf-8') as f:
        for l in dmz_filter_parser.read(f):
            assert len(l.level) == 3
            assert l.run_time is not None
            assert l.timestamp is not None
            assert l.msg is not None


@pytest.mark.api
def DmzFilterForeverParser_test():
    dmz_filter_parser = DmzFilterParser()
    with open(r'D:\workflow\ImTestPy\tests\data\dmz_log_temp\dmz_filter_forever.log.2025-12-08_17_20_30.407714842', 'r',
              encoding='utf-8') as f:
        for l in dmz_filter_parser.read(f):
            assert len(l.level) == 3
            assert l.run_time is not None
            assert l.timestamp is not None
            assert l.msg is not None


@pytest.mark.api
def DmzRecorderParser_test():
    dmz_filter_parser = DmzRecorderParser()
    with open(r'D:\workflow\ImTestPy\tests\data\dmz_log_temp\dmz_recorder.log.2025-12-08_17_20_29.262304157', 'r',
              encoding='utf-8') as f:
        for l in dmz_filter_parser.read(f):
            assert len(l.level) == 3
            assert l.run_time is not None
            assert l.timestamp is not None
            assert l.msg is not None


@pytest.mark.api
def DmzRecorderForeverParser_test():
    dmz_filter_parser = DmzRecorderParser()
    with open(r'D:\workflow\ImTestPy\tests\data\dmz_log_temp\dmz_recorder_forever.log.2025-12-08_17_20_29.263278583',
              'r',
              encoding='utf-8') as f:
        for l in dmz_filter_parser.read(f):
            assert len(l.level) == 3
            assert l.run_time is not None
            assert l.timestamp is not None
            assert l.msg is not None
