"""
@文件: logChecker.py
@作者: 雷小鸥
@日期: 2025/9/26 09:46
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
from abc import ABC, abstractmethod
from typing import Iterable, Optional, Type
import pyparsing as pp
from functools import cached_property

from .logger import logger


class LogField:
    def __init__(self, name=None):
        self.name = name

    def __set_name__(self, owner, name):
        # pyton 3.6+ auto set name
        if self.name is None:
            self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.get(self.name, '')


class BaseLogRecord(pp.ParseResults, ABC):
    def __str__(self):
        return self.msg


class BaseLogParser(ABC):
    def __init__(self):
        self._buffer = ''

    @property
    @abstractmethod
    def _record_cls(self) -> Type[BaseLogRecord]:
        pass

    @abstractmethod
    def _build_perse(self) -> pp.ParserElement:
        """
        测试时屏蔽此接口:
            return pp.SkipTo(pp.StringEnd())

        :return:
        """
        pass

    @cached_property
    def _structure(self) -> Optional[pp.ParserElement]:
        return self._build_perse()

    @abstractmethod
    def _preprocess(self, line: str) -> str:
        return line

    def __parse_block(self, block: str) -> BaseLogRecord | None:
        try:
            return self._record_cls(self._structure.parseString(block))
        except Exception as e:
            print()
            print()
            print(block)
            print()
            return None

    def read(self, iter_obj: Iterable[str]) -> Iterable[BaseLogRecord]:
        for line in iter_obj:
            block = self._preprocess(line)

            if block:
                _record = self.__parse_block(block)
                if _record:
                    yield _record

        yield from self.__flush_buffer()

    def __flush_buffer(self):
        if self._buffer:
            yield self.__parse_block(self._buffer)
            self._buffer = ''
