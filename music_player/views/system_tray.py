"""系统托盘"""

from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal, QObject


class SystemTray(QObject):
    """系统托盘图标"""
    
    # 信号
    play_pause_requested = Signal()
    next_requested = Signal()
    previous_requested = Signal()
    show_requested = Signal()
    quit_requested = Signal()
    
    def __init__(self, parent=None):
        """初始化系统托盘
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.parent_window = parent
        
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(parent)
        self.tray_icon.setToolTip("音乐播放器")
        
        # 创建菜单
        self._create_menu()
        
        # 连接信号
        self.tray_icon.activated.connect(self._on_activated)
    
    def _create_menu(self) -> None:
        """创建托盘菜单"""
        menu = QMenu()
        
        # 播放/暂停
        self.play_pause_action = QAction("▶ 播放", self)
        self.play_pause_action.triggered.connect(self.play_pause_requested.emit)
        menu.addAction(self.play_pause_action)
        
        # 上一首
        prev_action = QAction("⏮ 上一首", self)
        prev_action.triggered.connect(self.previous_requested.emit)
        menu.addAction(prev_action)
        
        # 下一首
        next_action = QAction("⏭ 下一首", self)
        next_action.triggered.connect(self.next_requested.emit)
        menu.addAction(next_action)
        
        menu.addSeparator()
        
        # 显示窗口
        show_action = QAction("🎵 显示窗口", self)
        show_action.triggered.connect(self.show_requested.emit)
        menu.addAction(show_action)
        
        # 退出
        quit_action = QAction("❌ 退出", self)
        quit_action.triggered.connect(self.quit_requested.emit)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
    
    def show(self) -> None:
        """显示托盘图标"""
        self.tray_icon.show()
    
    def hide(self) -> None:
        """隐藏托盘图标"""
        self.tray_icon.hide()
    
    def update_tooltip(self, text: str) -> None:
        """更新提示文本
        
        Args:
            text: 提示文本
        """
        self.tray_icon.setToolTip(text)
    
    def update_play_pause_action(self, is_playing: bool) -> None:
        """更新播放/暂停动作文本
        
        Args:
            is_playing: 是否正在播放
        """
        if is_playing:
            self.play_pause_action.setText("⏸ 暂停")
        else:
            self.play_pause_action.setText("▶ 播放")
    
    def _on_activated(self, reason) -> None:
        """托盘图标激活
        
        Args:
            reason: 激活原因
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # 单击托盘图标，显示/隐藏窗口
            self.show_requested.emit()
