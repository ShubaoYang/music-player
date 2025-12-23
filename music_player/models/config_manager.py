"""配置管理器"""

import os
import json
from typing import Dict, Any, Optional


class ConfigManager:
    """管理应用配置和持久化"""
    
    def __init__(self, config_dir: str = "~/.config/music-player"):
        """初始化配置管理器
        
        Args:
            config_dir: 配置目录路径
        """
        self.config_dir = os.path.expanduser(config_dir)
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.playlists_dir = os.path.join(self.config_dir, "playlists")
        self.log_file = os.path.join(self.config_dir, "music_player.log")
        self._config: Dict[str, Any] = {}
        
        # 确保目录存在
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """确保配置目录存在"""
        os.makedirs(self.config_dir, mode=0o755, exist_ok=True)
        os.makedirs(self.playlists_dir, mode=0o755, exist_ok=True)
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件
        
        Returns:
            配置字典
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            except Exception as e:
                print(f"加载配置失败: {e}")
                self._config = self._get_default_config()
        else:
            self._config = self._get_default_config()
        
        return self._config
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> None:
        """保存配置文件
        
        Args:
            config: 要保存的配置字典，如果为 None 则保存当前配置
        """
        if config is not None:
            self._config = config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        """
        self._config[key] = value
    
    def get_playlists_dir(self) -> str:
        """获取播放列表目录路径
        
        Returns:
            播放列表目录路径
        """
        return self.playlists_dir
    
    def get_log_file(self) -> str:
        """获取日志文件路径
        
        Returns:
            日志文件路径
        """
        return self.log_file
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置
        
        Returns:
            默认配置字典
        """
        return {
            "volume": 70,
            "playback_mode": "sequential",
            "window_geometry": None,
            "current_track_index": -1,
            "current_position": 0.0,
            "playlist": [],
            "equalizer": {
                "enabled": False,
                "bands": [0.0, 0.0, 0.0, 0.0, 0.0]
            }
        }
