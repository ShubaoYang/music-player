"""日志工具"""

import logging
import os
from datetime import datetime
from typing import Dict, Set


class ErrorDeduplicator:
    """错误去重器"""
    
    def __init__(self, time_window: int = 60):
        """初始化去重器
        
        Args:
            time_window: 时间窗口（秒）
        """
        self.time_window = time_window
        self._recent_errors: Dict[str, float] = {}
    
    def should_log(self, error_key: str) -> bool:
        """判断是否应该记录错误
        
        Args:
            error_key: 错误键
            
        Returns:
            是否应该记录
        """
        current_time = datetime.now().timestamp()
        
        if error_key in self._recent_errors:
            last_time = self._recent_errors[error_key]
            if current_time - last_time < self.time_window:
                return False
        
        self._recent_errors[error_key] = current_time
        return True
    
    def cleanup(self) -> None:
        """清理过期的错误记录"""
        current_time = datetime.now().timestamp()
        expired_keys = [
            key for key, timestamp in self._recent_errors.items()
            if current_time - timestamp >= self.time_window
        ]
        for key in expired_keys:
            del self._recent_errors[key]


class MusicPlayerLogger:
    """音乐播放器日志器"""
    
    def __init__(self, log_file: str):
        """初始化日志器
        
        Args:
            log_file: 日志文件路径
        """
        self.log_file = log_file
        self.deduplicator = ErrorDeduplicator()
        
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('MusicPlayer')
    
    def info(self, message: str) -> None:
        """记录信息
        
        Args:
            message: 信息内容
        """
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """记录警告
        
        Args:
            message: 警告内容
        """
        self.logger.warning(message)
    
    def error(self, message: str, error_type: str = "general") -> None:
        """记录错误（带去重）
        
        Args:
            message: 错误信息
            error_type: 错误类型
        """
        error_key = f"{error_type}:{message}"
        
        if self.deduplicator.should_log(error_key):
            self.logger.error(message)
        
        # 定期清理过期记录
        self.deduplicator.cleanup()
    
    def exception(self, message: str) -> None:
        """记录异常
        
        Args:
            message: 异常信息
        """
        self.logger.exception(message)
