from shared.logger import logs


class RecordLog:
    """旧日志入口兼容类，新结构统一使用 shared.logger.logs。"""

    def output_logging(self):
        """获取 logger 对象。"""
        return logs


apilog = RecordLog()
logs = apilog.output_logging()
