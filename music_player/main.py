"""音乐播放器主入口"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon

from .models.playback_engine import PlaybackEngine
from .models.playlist_manager import PlaylistManager
from .models.config_manager import ConfigManager
from .models.metadata_reader import MetadataReader
from .models.playback_mode import PlaybackMode
from .models.track import Track
from .controllers.player_controller import PlayerController
from .views.main_window import MainWindow
from .views.mini_window import MiniWindow
from .views.system_tray import SystemTray
from .utils.logger import MusicPlayerLogger


class MusicPlayerApp:
    """音乐播放器应用"""
    
    def __init__(self):
        """初始化应用"""
        # 获取或创建 Qt 应用
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        self.app.setApplicationName("音乐播放器")
        
        # 设置应用图标
        self._set_app_icon()
        
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
        
        # 创建迷你窗口
        self.mini_window = MiniWindow()
        
        # 为窗口设置图标
        self._set_window_icons()
        
        # 创建系统托盘
        self.system_tray = SystemTray(self.main_window)
        self.system_tray.show()
        
        # 当前显示的窗口模式
        self._is_mini_mode = False
        
        # 连接信号
        self._connect_signals()
        
        # 创建进度更新定时器
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._update_progress)
        self.progress_timer.start(100)
        
        # 恢复状态
        self._restore_state()
        
        self.logger.info("音乐播放器启动")
    
    def _set_app_icon(self) -> None:
        """设置应用图标"""
        # 获取图标文件路径
        icon_paths = [
            "assets/icon_512x512.png",  # 相对于项目根目录
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon_512x512.png"),  # 绝对路径
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                if not icon.isNull():
                    # 设置应用程序图标（影响 Dock 和程序栏）
                    self.app.setWindowIcon(icon)
                    print(f"✓ 已设置应用图标: {icon_path}")
                    return
        
        print("⚠️ 未找到应用图标文件")
    
    def _set_window_icons(self) -> None:
        """为窗口设置图标"""
        # 获取图标文件路径
        icon_paths = [
            "assets/icon_512x512.png",
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon_512x512.png"),
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                if not icon.isNull():
                    self.main_window.setWindowIcon(icon)
                    self.mini_window.setWindowIcon(icon)
                    return
    
    def _connect_signals(self) -> None:
        """连接信号"""
        # 主窗口控制信号
        self.main_window.play_pause_clicked.connect(
            self.controller.play_pause
        )
        self.main_window.prev_clicked.connect(
            self.controller.previous_track
        )
        self.main_window.next_clicked.connect(
            self.controller.next_track
        )
        self.main_window.seek_requested.connect(
            self.controller.seek
        )
        self.main_window.volume_changed.connect(
            self.controller.set_volume
        )
        
        # 窗口关闭信号
        self.main_window.window_closing.connect(
            self._save_state
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
        self.main_window.mini_mode_requested.connect(
            self._switch_to_mini_mode
        )
        
        # 迷你窗口信号
        self.mini_window.play_pause_clicked.connect(
            self.controller.play_pause
        )
        self.mini_window.prev_clicked.connect(
            self.controller.previous_track
        )
        self.mini_window.next_clicked.connect(
            self.controller.next_track
        )
        self.mini_window.volume_changed.connect(
            self.controller.set_volume
        )
        self.mini_window.restore_clicked.connect(
            self._switch_to_normal_mode
        )
        self.mini_window.close_clicked.connect(
            self._switch_to_normal_mode
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
        self.main_window.reset_progress()
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
            # 更新主窗口
            self.main_window.update_now_playing(
                track.title,
                track.artist,
                track.album,
                track.cover_art
            )
            self.main_window.playlist_view.update_current_track(index)
            
            # 更新迷你窗口
            self.mini_window.update_now_playing(
                track.title,
                track.artist,
                track.cover_art
            )
            
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
        self.main_window.update_play_button(is_playing)
        self.mini_window.update_play_button(is_playing)
        self.system_tray.update_play_pause_action(is_playing)
        
        # 只有在没有当前曲目时才清空界面
        if state == "stopped" and self.controller.current_index == -1:
            self.main_window.reset_progress()
            self.main_window.clear_now_playing()
            self.mini_window.clear_now_playing()
    
    def _on_error(self, message: str) -> None:
        """错误处理"""
        self.logger.error(message, "playback")
        QMessageBox.warning(self.main_window, "错误", message)
    
    def _update_progress(self) -> None:
        """更新进度"""
        if self.engine.is_playing() or self.engine.is_paused():
            position = self.engine.get_position()
            duration = self.engine.get_duration()
            self.main_window.update_progress(position, duration)
            
            # 更新迷你窗口时间显示
            current_time = Track.format_time(position)
            total_time = Track.format_time(duration)
            self.mini_window.update_time(current_time, total_time)
    
    def _toggle_window_visibility(self) -> None:
        """切换窗口可见性"""
        if self._is_mini_mode:
            # 迷你模式下，切换迷你窗口
            if self.mini_window.isVisible():
                self.mini_window.hide()
            else:
                self.mini_window.show()
                self.mini_window.activateWindow()
        else:
            # 正常模式下，切换主窗口
            if self.main_window.isVisible():
                self.main_window.hide()
            else:
                self.main_window.show()
                self.main_window.activateWindow()
    
    def _switch_to_mini_mode(self) -> None:
        """切换到迷你模式"""
        print(f"🔄 尝试切换到迷你模式，当前状态: _is_mini_mode={self._is_mini_mode}")
        
        if self._is_mini_mode:
            print("⚠️ 已经是迷你模式，跳过")
            return
        
        self._is_mini_mode = True
        
        # 同步当前状态到迷你窗口
        track = self.playlist_manager.get_track(self.controller.current_index)
        if track:
            self.mini_window.update_now_playing(
                track.title,
                track.artist,
                track.cover_art
            )
        
        # 同步播放状态
        is_playing = self.engine.is_playing()
        self.mini_window.update_play_button(is_playing)
        
        # 同步音量
        volume = self.main_window.volume_slider.value()
        self.mini_window.set_volume(volume)
        
        # 同步时间
        if self.engine.is_playing() or self.engine.is_paused():
            position = self.engine.get_position()
            duration = self.engine.get_duration()
            current_time = Track.format_time(position)
            total_time = Track.format_time(duration)
            self.mini_window.update_time(current_time, total_time)
        
        # 隐藏主窗口，显示迷你窗口
        self.main_window.hide()
        self.mini_window.show()
        
        print("✓ 已切换到迷你模式")
        self.logger.info("切换到迷你模式")
    
    def _switch_to_normal_mode(self) -> None:
        """切换到正常模式"""
        print(f"🔄 尝试切换到正常模式，当前状态: _is_mini_mode={self._is_mini_mode}")
        
        if not self._is_mini_mode:
            print("⚠️ 已经是正常模式，跳过")
            return
        
        self._is_mini_mode = False
        
        # 同步音量回主窗口
        volume = self.mini_window.volume_slider.value()
        self.main_window.volume_slider.setValue(volume)
        
        # 隐藏迷你窗口，显示主窗口
        self.mini_window.hide()
        self.main_window.show()
        self.main_window.activateWindow()
        
        print("✓ 已切换到正常模式")
        self.logger.info("切换到正常模式")
        self.main_window.show()
        self.main_window.activateWindow()
        
        self.logger.info("切换到正常模式")
    
    def _quit_application(self) -> None:
        """退出应用"""
        self._save_state()
        self.logger.info("音乐播放器退出")
        self.app.quit()
    
    def _restore_state(self) -> None:
        """恢复状态"""
        # 恢复播放列表和设置
        self.controller.restore_state()
        
        # 恢复音量 - 先设置引擎音量，再设置滑块（避免触发信号）
        volume = self.config_manager.get("volume", 70)
        self.controller.set_volume(volume / 100.0)
        self.main_window.volume_slider.blockSignals(True)
        self.main_window.volume_slider.setValue(volume)
        self.main_window.volume_slider.blockSignals(False)
        self.mini_window.volume_slider.blockSignals(True)
        self.mini_window.volume_slider.setValue(volume)
        self.mini_window.volume_slider.blockSignals(False)
        
        # 恢复播放模式
        mode_str = self.config_manager.get("playback_mode", "sequential")
        try:
            mode = PlaybackMode(mode_str)
            self.main_window.set_playback_mode(mode)
        except ValueError:
            pass
        
        # 如果有恢复的曲目，更新界面显示
        if self.controller.current_index >= 0:
            track = self.playlist_manager.get_track(self.controller.current_index)
            if track:
                self.main_window.update_now_playing(
                    track.title,
                    track.artist,
                    track.album,
                    track.cover_art
                )
                self.main_window.playlist_view.update_current_track(self.controller.current_index)
                
                # 更新进度显示
                saved_position = self.config_manager.get("current_position", 0.0)
                self.main_window.update_progress(saved_position, track.duration)
                
                # 确保播放按钮显示为"播放"（因为恢复后是暂停状态）
                self.main_window.update_play_button(False)
                
                self.logger.info(f"恢复状态: {track.get_display_name()}, 位置={saved_position:.2f}秒")
    
    def _save_state(self) -> None:
        """保存状态"""
        # 保存音量
        volume = self.main_window.volume_slider.value()
        self.config_manager.set("volume", volume)
        
        # 保存播放模式
        mode = self.playlist_manager.get_play_mode()
        self.config_manager.set("playback_mode", mode.value)
        
        # 保存播放列表
        tracks = self.playlist_manager.get_all_tracks()
        playlist_paths = [track.file_path for track in tracks]
        self.config_manager.set("playlist", playlist_paths)
        
        # 保存当前曲目和播放位置
        self.config_manager.set("current_track_index", self.controller.current_index)
        
        # 获取当前播放位置
        current_position = 0.0
        if self.engine.is_playing() or self.engine.is_paused():
            current_position = self.engine.get_position()
        self.config_manager.set("current_position", current_position)
        
        # 保存配置
        self.config_manager.save_config()
        self.logger.info(f"保存状态: 曲目索引={self.controller.current_index}, 播放位置={current_position:.2f}秒")
    
    def run(self) -> int:
        """运行应用
        
        Returns:
            退出代码
        """
        # 默认显示主窗口
        self.main_window.show()
        return self.app.exec_()


def main():
    """主函数"""
    app = MusicPlayerApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
