"""
日志系统模块 - 统一的日志记录
"""
import logging
import os
import sys
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler


# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 默认日志目录
DEFAULT_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")


class DictationLogger:
    """听写软件日志管理器"""

    _instance: Optional['DictationLogger'] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if DictationLogger._initialized:
            return

        self.log_dir = DEFAULT_LOG_DIR
        self.log_level = logging.INFO
        self.loggers = {}

        # 创建日志目录
        os.makedirs(self.log_dir, exist_ok=True)

        # 初始化根日志器
        self._setup_root_logger()

        DictationLogger._initialized = True

    def _setup_root_logger(self):
        """设置根日志器"""
        root_logger = logging.getLogger("dictation")
        root_logger.setLevel(self.log_level)

        # 清除现有处理器
        root_logger.handlers.clear()

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
        root_logger.addHandler(console_handler)

        # 文件处理器（轮转日志）
        log_file = os.path.join(self.log_dir, "dictation.log")
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
        root_logger.addHandler(file_handler)

        # 错误日志单独文件
        error_file = os.path.join(self.log_dir, "error.log")
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
        root_logger.addHandler(error_handler)

    def get_logger(self, name: str) -> logging.Logger:
        """获取指定名称的日志器"""
        if name in self.loggers:
            return self.loggers[name]

        logger = logging.getLogger(f"dictation.{name}")
        logger.setLevel(self.log_level)
        self.loggers[name] = logger
        return logger

    def set_level(self, level: int):
        """设置日志级别"""
        self.log_level = level
        root_logger = logging.getLogger("dictation")
        root_logger.setLevel(level)
        for logger in self.loggers.values():
            logger.setLevel(level)

    def set_debug_mode(self, enabled: bool = True):
        """设置调试模式"""
        if enabled:
            self.set_level(logging.DEBUG)
        else:
            self.set_level(logging.INFO)


# 全局日志管理器实例
_logger_manager: Optional[DictationLogger] = None


def get_logger(name: str = "main") -> logging.Logger:
    """获取日志器的便捷函数"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = DictationLogger()
    return _logger_manager.get_logger(name)


def set_log_level(level: int):
    """设置日志级别的便捷函数"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = DictationLogger()
    _logger_manager.set_level(level)


def enable_debug():
    """启用调试模式"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = DictationLogger()
    _logger_manager.set_debug_mode(True)


def disable_debug():
    """禁用调试模式"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = DictationLogger()
    _logger_manager.set_debug_mode(False)


# 预定义的模块日志器
class ModuleLoggers:
    """模块日志器集合"""

    @staticmethod
    def ocr() -> logging.Logger:
        return get_logger("ocr")

    @staticmethod
    def tts() -> logging.Logger:
        return get_logger("tts")

    @staticmethod
    def corrector() -> logging.Logger:
        return get_logger("corrector")

    @staticmethod
    def cache() -> logging.Logger:
        return get_logger("cache")

    @staticmethod
    def vocabulary() -> logging.Logger:
        return get_logger("vocabulary")

    @staticmethod
    def history() -> logging.Logger:
        return get_logger("history")

    @staticmethod
    def handwriting() -> logging.Logger:
        return get_logger("handwriting")

    @staticmethod
    def app() -> logging.Logger:
        return get_logger("app")


# 日志装饰器
def log_function_call(logger_name: str = "main"):
    """函数调用日志装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name)
            logger.debug(f"调用函数: {func.__name__}, 参数: args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"函数 {func.__name__} 返回: {type(result)}")
                return result
            except Exception as e:
                logger.error(f"函数 {func.__name__} 异常: {e}", exc_info=True)
                raise
        return wrapper
    return decorator


def log_performance(logger_name: str = "main"):
    """性能日志装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            logger = get_logger(logger_name)
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(f"函数 {func.__name__} 执行时间: {elapsed:.3f}秒")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"函数 {func.__name__} 执行失败，耗时: {elapsed:.3f}秒, 错误: {e}")
                raise
        return wrapper
    return decorator


if __name__ == "__main__":
    # 测试日志系统
    logger = get_logger("test")

    logger.debug("这是调试信息")
    logger.info("这是普通信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")

    # 测试模块日志器
    ocr_logger = ModuleLoggers.ocr()
    ocr_logger.info("OCR模块日志测试")

    # 测试装饰器
    @log_function_call("test")
    @log_performance("test")
    def test_function(x, y):
        return x + y

    result = test_function(1, 2)
    print(f"测试函数结果: {result}")
