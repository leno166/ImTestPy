"""
@文件: logWatcher.py
@作者: 雷小鸥
@日期: 2025/12/9 16:27
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
from typing import Type

import pyparsing as pp
from .logCheckBase import LogField, BaseLogRecord, BaseLogParser


class DmzLogRecord(BaseLogRecord):
    level = LogField()
    run_time = LogField()
    timestamp = LogField()
    msg = LogField()


# ====================================================================================================================
# dmz fcl log
# ====================================================================================================================
class DmzFclParser(BaseLogParser):
    @property
    def _record_cls(self) -> Type[BaseLogRecord]:
        return DmzLogRecord

    def _preprocess(self, line: str) -> str:
        return line.replace('\x00', '')

    def _build_perse(self) -> pp.ParserElement:
        # 级别
        level = pp.Word(pp.alphas.upper(), exact=3)('level')

        # 运行时间
        run_time = pp.Word(pp.nums)('run_time')

        # 时间戳
        timestamp = pp.Regex(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+')('timestamp')

        # 消息 - 冒号后面的所有内容
        # 使用SkipTo可以更安全地处理冒号
        msg = pp.SkipTo(pp.lineEnd)('msg')

        return (
                pp.Suppress('[dmz_fcl]') + pp.Suppress('[NORMAL]')
                + pp.Suppress('[') + level + pp.Suppress(']')
                + pp.Suppress('[') + run_time + pp.Suppress(']')
                + pp.Suppress('[') + timestamp + pp.Suppress(']:')
                + msg
        )


# ====================================================================================================================
# dmz filter log & dmz filter forever log
# ====================================================================================================================
class DmzFilterParser(BaseLogParser):
    def __init__(self):
        super().__init__()

        self.first_line = True

    @property
    def _record_cls(self) -> Type[BaseLogRecord]:
        return DmzLogRecord

    def _preprocess(self, line: str) -> str:
        line = line.replace('\x00', '').strip() + '\n'

        if line.startswith('[dmz_filter][NORMAL]'):
            if self.first_line:
                self._buffer = line
                self.first_line = False
                return ''

            completed, self._buffer = self._buffer, line
            return completed

        else:
            self._buffer += line
            return ''

    def _build_perse(self) -> pp.ParserElement:
        # 级别
        level = pp.Word(pp.alphas.upper(), exact=3)('level')

        # 运行时间
        run_time = pp.Word(pp.nums)('run_time')

        # 时间戳
        timestamp = pp.Regex(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+')('timestamp')

        # 消息 - 冒号后面的所有内容
        # 使用SkipTo可以更安全地处理冒号
        msg = pp.SkipTo(pp.lineEnd)('msg')

        return (
                pp.Suppress('[dmz_filter]') + pp.Suppress('[NORMAL]')
                + pp.Suppress('[') + level + pp.Suppress(']')
                + pp.Suppress('[') + run_time + pp.Suppress(']')
                + pp.Suppress('[') + timestamp + pp.Suppress(']:')
                + msg
        )


# ====================================================================================================================
# dmz recorder log & dmz recorder forever log
# ====================================================================================================================
class DmzRecorderParser(BaseLogParser):
    def __init__(self):
        super().__init__()

        self.first_line = True

    @property
    def _record_cls(self) -> Type[BaseLogRecord]:
        return DmzLogRecord

    def _preprocess(self, line: str) -> str:
        line = line.replace('\x00', '').strip() + '\n'

        if line.startswith('[dmz_filter][NORMAL]'):
            if self.first_line:
                self._buffer = line
                self.first_line = False
                return ''

            completed, self._buffer = self._buffer, line
            return completed

        else:
            self._buffer += line
            return ''

    def _build_perse(self) -> pp.ParserElement:
        # 级别
        level = pp.Word(pp.alphas.upper(), exact=3)('level')

        # 运行时间
        run_time = pp.Word(pp.nums)('run_time')

        # 时间戳
        timestamp = pp.Regex(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+')('timestamp')

        # 消息 - 冒号后面的所有内容
        # 使用SkipTo可以更安全地处理冒号
        msg = pp.SkipTo(pp.lineEnd)('msg')

        return (
                pp.Suppress('[dmz_recorder]') + pp.Suppress('[NORMAL]')
                + pp.Suppress('[') + level + pp.Suppress(']')
                + pp.Suppress('[') + run_time + pp.Suppress(']')
                + pp.Suppress('[') + timestamp + pp.Suppress(']:')
                + msg
        )
