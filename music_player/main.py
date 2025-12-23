"""音乐播放器主入口"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer

from .models.playback_engine import PlaybackEngine
from .models.playlist_manager import PlaylistManager
from .models.config_manager import ConfigManager
from .models.metadata_reader import MetadataReader
from .models.playback_mode import PlaybackMode
from .controllers.player_controller import PlayerController
from .views.main_window import MainWindow
from .views.system_tray import SystemTray
from .utils.logger import MusicPlayerLogger


class MusicPlayerApp:
    """音乐播放器应用"""
    
    def __init__(self):
        """初始化应用"""
        # 创建 Qt 应用
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("音乐播放器")
        
        # 初始化组件
        self.config_manager = ConfigManager()
        self.logger = MusicPlayerLogger(self.config_manager.get_log_file())
        
        self.engine = PlaybackEngine()
        self.playlist_manager = PlaylistManager()
        self.metadata_reader = MetadataReader()
        
        self.controller = PlayerController(
            self.engine,
            self.playlist_manager,
            self.config_manager,
            self.metadata_reader
        )
        
        # 创建主窗口
        self.main_window = MainWindow()
        
        # 创建系统托盘
        self.system_tray = SystemTray(self.main_window)
        self.system_tray.show()
        
        # 连接信号
        self._connect_signals()
        
        # 创建进度更新定时器
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._update_progress)
        self.progress_timer.start(100)
        
        # 恢复状态
        self._restore_state()
        
        self.logger.info("音乐播放器启动")
    
    def _connect_signals(self) -> None:
        """连接信号"""
        # 控制面板信号
        self.main_window.control_panel.play_pause_clicked.connect(
            self.controller.play_pause
        )
        self.main_window.control_panel.stop_clicked.connect(
            self.controller.stop
        )
        self.main_window.control_panel.prev_clicked.connect(
            self.controller.previous_track
        )
        self.main_window.control_panel.next_clicked.connect(
            self.controller.next_track
        )
        self.main_window.control_panel.seek_requested.connect(
            self.controller.seek
        )
        self.main_window.control_panel.volume_changed.connect(
            self.controller.set_volume
        )
        
        # 播放列表信号
        self.main_window.playlist_view.track_double_clicked.connect(
            self.controller.play_track_at_index
        )
        self.main_window.playlist_view.track_delete_requested.connect(
            self.controller.remove_track
        )
        
        # 主窗口信号
        self.main_window.add_files_requested.connect(
            self._on_add_files
        )
        self.main_window.add_folder_requested.connect(
            self._on_add_folder
        )
        self.main_window.clear_playlist_requested.connect(
            self._on_clear_playlist
        )
        self.main_window.save_playlist_requested.connect(
            self._on_save_playlist
        )
        self.main_window.load_playlist_requested.connect(
            self._on_load_playlist
        )
        
        # 播放模式按钮
        self.main_window.sequential_btn.clicked.connect(
            lambda: self.controller.set_play_mode(PlaybackMode.SEQUENTIAL)
        )
        self.main_window.loop_btn.clicked.connect(
            lambda: self.controller.set_play_mode(PlaybackMode.LOOP)
        )
        self.main_window.shuffle_btn.clicked.connect(
            lambda: self.controller.set_play_mode(PlaybackMode.SHUFFLE)
        )
        self.main_window.single_btn.clicked.connect(
            lambda: self.controller.set_play_mode(PlaybackMode.SINGLE_REPEAT)
        )
        
        # 控制器信号
        self.controller.track_changed.connect(self._on_track_changed)
        self.controller.error_occurred.connect(self._on_error)
        
        # 播放列表管理器信号
        self.playlist_manager.playlist_changed.connect(self._on_playlist_changed)
        
        # 播放引擎信号
        self.engine.state_changed.connect(self._on_state_changed)
        
        # 系统托盘信号
        self.system_tray.play_pause_requested.connect(self.controller.play_pause)
        self.system_tray.next_requested.connect(self.controller.next_track)
        self.system_tray.previous_requested.connect(self.controller.previous_track)
        self.system_tray.show_requested.connect(self._toggle_window_visibility)
        self.system_tray.quit_requested.connect(self._quit_application)
    
    def _on_add_files(self, files: list) -> None:
        """添加文件"""
        self.controller.add_tracks(files)
        self.logger.info(f"添加了 {len(files)} 个文件")
    
    def _on_add_folder(self, folder: str) -> None:
        """添加文件夹"""
        audio_extensions = ['.mp3', '.wav', '.ogg', '.flac']
        files = []
        
        for root, dirs, filenames in os.walk(folder):
            for filename in filenames:
                if os.path.splitext(filename)[1].lower() in audio_extensions:
                    files.append(os.path.join(root, filename))
        
        if files:
            self.controller.add_tracks(files)
            QMessageBox.information(
                self.main_window,
                "成功",
                f"已添加 {len(files)} 首歌曲"
            )
            self.logger.info(f"从文件夹添加了 {len(files)} 个文件")
        else:
            QMessageBox.warning(
                self.main_window,
                "提示",
                "该文件夹中没有找到音频文件"
            )
    
    def _on_clear_playlist(self) -> None:
        """清空播放列表"""
        self.controller.stop()
        self.playlist_manager.clear()
        self.main_window.control_panel.reset_progress()
        self.main_window.clear_now_playing()
        self.logger.info("清空播放列表")
    
    def _on_save_playlist(self, file_path: str) -> None:
        """保存播放列表"""
        name = os.path.splitext(os.path.basename(file_path))[0]
        self.playlist_manager.save_playlist(name, file_path)
        QMessageBox.information(
            self.main_window,
            "成功",
            "播放列表已保存"
        )
        self.logger.info(f"保存播放列表: {file_path}")
    
    def _on_load_playlist(self, file_path: str) -> None:
        """加载播放列表"""
        track_paths = self.playlist_manager.load_playlist(file_path)
        if track_paths:
            self.controller.add_tracks(track_paths)
            QMessageBox.information(
                self.main_window,
                "成功",
                f"已加载 {len(track_paths)} 首歌曲"
            )
            self.logger.info(f"加载播放列表: {file_path}")
    
    def _on_track_changed(self, index: int) -> None:
        """曲目变化"""
        track = self.playlist_manager.get_track(index)
        if track:
            self.main_window.update_now_playing(
                track.title,
                track.artist,
                track.album,
                track.cover_art
            )
            self.main_window.playlist_view.update_current_track(index)
            
            # 更新托盘提示
            tooltip = f"正在播放: {track.get_display_name()}"
            self.system_tray.update_tooltip(tooltip)
            
            self.logger.info(f"播放: {track.get_display_name()}")
    
    def _on_playlist_changed(self) -> None:
        """播放列表变化"""
        tracks = self.playlist_manager.get_all_tracks()
        self.main_window.playlist_view.set_tracks(tracks)
    
    def _on_state_changed(self, state: str) -> None:
        """播放状态变化"""
        is_playing = state == "playing"
        self.main_window.control_panel.update_play_button(is_playing)
        self.system_tray.update_play_pause_action(is_playing)
        
        if state == "stopped":
            self.main_window.control_panel.reset_progress()
            self.main_window.clear_now_playing()
    
    def _on_error(self, message: str) -> None:
        """错误处理"""
        self.logger.error(message, "playback")
        QMessageBox.warning(self.main_window, "错误", message)
    
    def _update_progress(self) -> None:
        """更新进度"""
        if self.engine.is_playing() or self.engine.is_paused():
            position = self.engine.get_position()
            duration = self.engine.get_duration()
            self.main_window.control_panel.update_progress(position, duration)
    
    def _toggle_window_visibility(self) -> None:
        """切换窗口可见性"""
        if self.main_window.isVisible():
            self.main_window.hide()
        else:
            self.main_window.show()
            self.main_window.activateWindow()
    
    def _quit_application(self) -> None:
        """退出应用"""
        self._save_state()
        self.logger.info("音乐播放器退出")
        self.app.quit()
    
    def _restore_state(self) -> None:
        """恢复状态"""
        # 恢复播放列表和设置
        self.controller.restore_state()
        
        # 恢复音量
        volume = self.config_manager.get("volume", 70)
        self.main_window.control_panel.set_volume(volume)
        self.controller.set_volume(volume / 100.0)
        
        # 恢复播放模式
        mode_str = self.config_manager.get("playback_mode", "sequential")
        try:
            mode = PlaybackMode(mode_str)
            self.main_window.set_playback_mode(mode)
        except ValueError:
            pass
        
        # 恢复窗口几何
        geometry = self.config_manager.get("window_geometry")
        if geometry:
            # 这里可以恢复窗口位置和大小
            pass
    
    def _save_state(self) -> None:
        """保存状态"""
        # 保存音量
        volume = self.main_window.control_panel.volume_slider.value()
        self.config_manager.set("volume", volume)
        
        # 保存播放模式
        mode = self.playlist_manager.get_play_mode()
        self.config_manager.set("playback_mode", mode.value)
        
        # 保存播放列表
        tracks = self.playlist_manager.get_all_tracks()
        playlist_paths = [track.file_path for track in tracks]
        self.config_manager.set("playlist", playlist_paths)
        
        # 保存当前曲目
        self.config_manager.set("current_track_index", self.controller.current_index)
        
        # 保存配置
        self.config_manager.save_config()
    
    def run(self) -> int:
        """运行应用
        
        Returns:
            退出代码
        """
        self.main_window.show()
        return self.app.exec_()


def main():
    """主函数"""
    app = MusicPlayerApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
