# -*- coding: utf-8 -*-
"""统一日志入口。"""
import logging
import time
from logging.handlers import RotatingFileHandler

from config.settings import LOG_DIR, LOG_LEVEL, STREAM_LOG_LEVEL


def _build_logger():
    logger = logging.getLogger('clmerp')
    if logger.handlers:
        return logger

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger.setLevel(LOG_LEVEL)
    formatter = logging.Formatter(
        '%(levelname)s - %(asctime)s - %(filename)s:%(lineno)d -[%(module)s:%(funcName)s] - %(message)s'
    )

    log_file = LOG_DIR / f'test.{time.strftime("%Y%m%d")}.log'
    file_handler = RotatingFileHandler(
        filename=str(log_file),
        mode='a',
        maxBytes=5242880,
        backupCount=7,
        encoding='utf-8',
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(STREAM_LOG_LEVEL)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


logs = _build_logger()
