# -*- coding: utf-8 -*-

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QLineEdit, QGroupBox, QFormLayout, QFileDialog,
    QMessageBox, QSplitter, QProgressDialog, QCheckBox, QTextEdit,
    QAction, QStatusBar, QMenu, QMenuBar, QComboBox, QFrame,
    QSizePolicy, QGraphicsDropShadowEffect, QSlider
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread, QPoint, QRect, QTimer, QEvent
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QPainterPath, QRegion

import taglib


# ==================== 主题常量（摘自 CMC） ====================
THEMES = {
    'light': {
        'display_name': '亮色',
        'primary': '#4A90D9',
        'primary_light': '#5DADE2',
        'primary_dark': '#357ABD',
        'background': '#F5F7FA',
        'content_rgb': '200,225,245',
        'surface': '#FFFFFF',
        'text': '#2C3E50',
        'title_text': '#2C3E50',
        'text_secondary': '#5D6D7E',
        'border': '#BDC3C7',
        'title_bar': '#E8F0FE',
        'hover': '#D5D8DC',
        'selected': '#4A90D9',
        'shadow': 'rgba(0,0,0,30)',
        'progress_gradient': 'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4A90D9, stop:1 #7B2FFC)',
        'surface_rgb': '255,255,255',
    },
    'dark': {
        'display_name': '暗色',
        'primary': '#4A90D9',
        'primary_light': '#5DADE2',
        'primary_dark': '#357ABD',
        'background': '#2C3E50',
        'content_rgb': '44,62,80',
        'surface': '#34495E',
        'text': '#ECF0F1',
        'title_text': '#ECF0F1',
        'text_secondary': '#BDC3C7',
        'border': '#5D6D7E',
        'title_bar': '#34495E',
        'hover': '#5D6D7E',
        'selected': '#4A90D9',
        'shadow': 'rgba(255,255,255,30)',
        'progress_gradient': 'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4A90D9, stop:1 #7B2FFC)',
        'surface_rgb': '52,73,94',
    },
}

# ==================== 全局样式生成器（摘自 CMC utils） ====================
def get_global_stylesheet(theme_name: str = 'light', bg_opacity: float = 0.85) -> str:
    """生成完整的 QSS 样式表，支持主题和透明度（修复大括号转义）"""
    colors = THEMES.get(theme_name, THEMES['light'])
    alpha = int(255 * max(0.5, min(1.0, bg_opacity)))
    content_bg = f"rgba({colors['content_rgb']},{alpha})"
    colors_with_alpha = colors.copy()
    colors_with_alpha['content_bg'] = content_bg

    template = """
    /* 全局基础 */
    QWidget {{
        font-family: "Microsoft YaHei", "PingFang SC", "Helvetica Neue", sans-serif;
        font-size: 12px;
        color: {text};
    }}
    #musicTagEditor {{
        background-color: {background};
        border-radius: 8px;
    }}
    #titleBar {{
        background-color: {title_bar};
        border-radius: 8px 8px 0 0;
        border-bottom: 1px solid {border};
    }}
    #titleBar QLabel {{
        background: transparent;
        font-size: 14px;
        font-weight: bold;
        color: {title_text};
    }}
    #titleMinButton, #titleMaxButton, #titleCloseButton {{
        background-color: transparent;
        border: none;
        border-radius: 4px;
        font-size: 16px;
        font-weight: bold;
        color: {text};
    }}
    #titleMinButton:hover {{ background-color: {hover}; }}
    #titleMaxButton:hover {{ background-color: {hover}; }}
    #titleCloseButton:hover {{ background-color: #E74C3C; color: white; }}
    #contentWidget {{
        background-color: {content_bg};
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }}
    QGroupBox {{
        font-weight: bold;
        border: 1px solid {border};
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 10px;
        color: {text};
        background-color: transparent;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
        color: {text};
    }}
    QTableWidget {{
        background-color: {surface};
        alternate-background-color: {hover};
        border: 1px solid {border};
        border-radius: 6px;
        gridline-color: {border};
        outline: none;
    }}
    QTableWidget::item {{
        padding: 6px;
        color: {text};
        border: none;
    }}
    QTableWidget::item:selected {{
        background-color: {selected};
        color: white;
    }}
    QTableWidget::item:hover:!selected {{
        background-color: rgba(74,144,217,0.2);
    }}
    QHeaderView::section {{
        background-color: {primary};
        color: white;
        padding: 6px;
        border: none;
        font-weight: bold;
    }}
    QPushButton {{
        background-color: {hover};
        color: {text};
        border: 1px solid {border};
        border-radius: 4px;
        padding: 6px 14px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: {border};
    }}
    QPushButton:pressed {{
        background-color: {primary};
        color: white;
    }}
    QPushButton#saveButton {{
        background-color: {primary};
        color: white;
        border: none;
    }}
    QPushButton#saveButton:hover {{
        background-color: {primary_dark};
    }}
    QPushButton#dangerButton {{
        background-color: #E67E22;
        color: white;
        border: none;
    }}
    QPushButton#dangerButton:hover {{
        background-color: #D35400;
    }}
    QLineEdit {{
        background-color: {surface};
        border: 1px solid {border};
        border-radius: 4px;
        padding: 5px 8px;
        color: {text};
        selection-background-color: {primary};
    }}
    QLineEdit:focus {{
        border-color: {primary};
    }}
    QTextEdit {{
        background-color: {surface};
        border: 1px solid {border};
        border-radius: 4px;
        color: {text};
    }}
    QCheckBox {{
        color: {text};
        spacing: 5px;
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: rgba(160,160,160,180);
        border-radius: 4px;
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
        background: transparent;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: transparent;
    }}
    QScrollBar:horizontal {{
        background: transparent;
        height: 8px;
        margin: 0px;
    }}
    QScrollBar::handle:horizontal {{
        background: rgba(160,160,160,180);
        border-radius: 4px;
        min-width: 20px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
        background: transparent;
    }}
    QProgressBar {{
        border: 1px solid {border};
        border-radius: 4px;
        background-color: {surface};
        text-align: center;
        color: {text};
        font-weight: bold;
    }}
    QProgressBar::chunk {{
        background-color: {primary};
        border-radius: 4px;
    }}
    QStatusBar {{
        background-color: {title_bar};
        color: {text};
        border-top: 1px solid {border};
    }}
    QMenu {{
        background-color: {surface};
        border: 1px solid {border};
        border-radius: 6px;
    }}
    QMenu::item {{
        padding: 6px 20px;
        color: {text};
    }}
    QMenu::item:selected {{
        background-color: {primary};
        color: white;
    }}
    QComboBox {{
        background-color: {surface};
        border: 1px solid {border};
        border-radius: 4px;
        padding: 4px 8px;
        color: {text};
    }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left: 1px solid {border};
        border-top-right-radius: 4px;
        border-bottom-right-radius: 4px;
        background: {hover};
    }}
    QComboBox QAbstractItemView {{
        border: 1px solid {border};
        border-radius: 4px;
        background: {surface};
        selection-background-color: {primary};
        selection-color: white;
    }}
    /* 滑块样式*/
    QSlider::groove:horizontal {{
        height: 6px;
        background: {border};
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: {primary};
        width: 14px;
        height: 14px;
        margin: -4px 0;
        border-radius: 7px;
    }}
    QSlider::sub-page:horizontal {{
        background: {primary};
        border-radius: 3px;
    }}
    /* 滚动条滑块在暗色下稍亮 */
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
        background: rgba(200,200,200,150);
    }}
    QPushButton#menuButton {{
        background-color: transparent;
        border: none;
        border-radius: 4px;
        padding: 4px 8px;
        color: {text};
        font-weight: normal;
    }}
    QPushButton#menuButton:hover {{
        background-color: {hover};
    }}
    /* 弹窗（QMessageBox、QDialog）适配主题 */
    QDialog, QMessageBox {{
        background-color: {background};
        color: {text};
    }}
    QMessageBox QLabel {{
        color: {text};
    }}
    QDialog QPushButton, QMessageBox QPushButton {{
        background-color: {surface};
        color: {text};
        border: 1px solid {border};
    }}
    QDialog QPushButton:hover, QMessageBox QPushButton:hover {{
        background-color: {hover};
    }}
    """
    return template.format(**colors_with_alpha)


# ==================== 编码工具函数 ====================
def decode_tag_value(value, encoding: str) -> str:
    if not value:
        return value
    if isinstance(value, str):
        try:
            raw_bytes = value.encode('latin1')
            return raw_bytes.decode(encoding)
        except (UnicodeDecodeError, UnicodeEncodeError):
            return value
    elif isinstance(value, bytes):
        try:
            return value.decode(encoding)
        except UnicodeDecodeError:
            return value.decode('utf-8', errors='replace')
    return value


def encode_tag_value(value: str, encoding: str) -> str:
    if not value:
        return value
    try:
        return value.encode(encoding).decode('latin1')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return value


def decode_tags(tags: dict, encoding: str) -> dict:
    if not encoding or encoding == 'UTF-8':
        return tags
    decoded = {}
    for key, values in tags.items():
        if isinstance(values, list):
            decoded[key] = [decode_tag_value(v, encoding) for v in values]
        else:
            decoded[key] = decode_tag_value(values, encoding)
    return decoded


def encode_tags_for_save(tags: dict, encoding: str) -> dict:
    if not encoding or encoding == 'UTF-8':
        return tags
    encoded = {}
    for key, values in tags.items():
        if isinstance(values, list):
            encoded[key] = [encode_tag_value(v, encoding) for v in values]
        else:
            encoded[key] = encode_tag_value(values, encoding)
    return encoded


# ==================== 后台加载线程 ====================
class LoadFilesThread(QThread):
    progress = pyqtSignal(int, int)
    file_loaded = pyqtSignal(str, dict, int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, file_paths, encoding: str = 'UTF-8'):
        super().__init__()
        self.file_paths = file_paths
        self.encoding = encoding
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def set_encoding(self, encoding: str):
        self.encoding = encoding

    def run(self):
        total = len(self.file_paths)
        for idx, file_path in enumerate(self.file_paths):
            if self._is_cancelled:
                break
            try:
                with taglib.File(file_path) as song:
                    tags = dict(song.tags)
                    if self.encoding and self.encoding != 'UTF-8':
                        tags = decode_tags(tags, self.encoding)
                    length = int(song.length) if song.length is not None else 0
                    self.file_loaded.emit(file_path, tags, length)
            except Exception as e:
                self.error.emit(f"读取失败: {file_path}\n{str(e)}")
            self.progress.emit(idx + 1, total)
        self.finished.emit()


# ==================== 主窗口 ====================
class MusicTagEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        # 无边框 + 透明背景
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName("musicTagEditor")

        self.files_data = {}
        self.current_file = None
        self.load_thread = None
        self.is_loading = False
        self.current_theme = 'light'
        self.bg_opacity = 0.85
        self.current_encoding = 'UTF-8'

        # 拖拽相关
        self.drag_pos = QPoint()
        self.dragging = False

        self._init_ui()
        self._setup_actions()
        self._setup_statusbar()

        # 加载设置（需在 UI 构建后，应用主题前）
        self.load_settings()

        # 应用主题（会使用加载的 self.current_theme 和 self.bg_opacity）
        self._apply_theme(self.current_theme)

    # ---------- 配置管理 ----------
    def _get_config_dir(self):
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        return os.path.join(base_dir, '.CME')

    def _get_config_path(self):
        return os.path.join(self._get_config_dir(), 'config.json')

    def load_settings(self):
        config_path = self._get_config_path()
        if not os.path.exists(config_path):
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 主题
            theme = config.get('theme', 'light')
            if theme in ('light', 'dark'):
                self.current_theme = theme

            # 编码
            encoding = config.get('encoding', 'UTF-8')
            self.current_encoding = encoding
            self.encoding_combo.blockSignals(True)
            idx = self.encoding_combo.findText(encoding)
            if idx >= 0:
                self.encoding_combo.setCurrentIndex(idx)
            self.encoding_combo.blockSignals(False)

            # 透明度 (存储为整数百分比 50~100)
            opacity = config.get('bg_opacity', 85)
            if 50 <= opacity <= 100:
                self.bg_opacity = opacity / 100.0
                self.opacity_slider.blockSignals(True)
                self.opacity_slider.setValue(opacity)
                self.opacity_slider.blockSignals(False)
                self.opacity_label.setText(f"{opacity}%")

            # 窗口几何和最大化
            maximized = config.get('maximized', False)
            geometry = config.get('geometry')
            if maximized:
                self.showMaximized()
            elif geometry and isinstance(geometry, dict):
                x = geometry.get('x')
                y = geometry.get('y')
                w = geometry.get('width')
                h = geometry.get('height')
                if all(v is not None for v in (x, y, w, h)):
                    self.setGeometry(x, y, w, h)
        except Exception:
            pass

    def save_settings(self):
        config_dir = self._get_config_dir()
        os.makedirs(config_dir, exist_ok=True)
        config_path = self._get_config_path()

        config = {
            'theme': self.current_theme,
            'encoding': self.current_encoding,
            'bg_opacity': int(self.bg_opacity * 100),
            'maximized': self.isMaximized(),
            'geometry': {
                'x': self.x(),
                'y': self.y(),
                'width': self.width(),
                'height': self.height()
            }
        }
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    # ---------- UI 构建 ----------
    def _init_ui(self):
        self.setWindowTitle("📝 音乐标签编辑器")
        self.setMinimumSize(1200, 750)
        self.resize(1200, 750)

        # 主容器
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 标题栏
        self.title_bar = QWidget()
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setFixedHeight(50)
        # 安装事件过滤器以捕捉双击
        self.title_bar.installEventFilter(self)
        # 鼠标事件用于拖动
        self.title_bar.mousePressEvent = self._title_mouse_press
        self.title_bar.mouseMoveEvent = self._title_mouse_move
        self.title_bar.mouseReleaseEvent = self._title_mouse_release

        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.setSpacing(8)

        # 图标/标题
        icon_label = QLabel("📝")
        title_layout.addWidget(icon_label)

        title_label = QLabel("音乐标签编辑器")
        title_layout.addWidget(title_label)

        # 菜单按钮
        self.btn_menu_file = QPushButton("文件")
        self.btn_menu_file.setObjectName("menuButton")
        self.btn_menu_file.setFixedSize(50, 28)
        self.btn_menu_file.clicked.connect(self._show_file_menu)
        title_layout.addWidget(self.btn_menu_file)

        self.btn_menu_edit = QPushButton("编辑")
        self.btn_menu_edit.setObjectName("menuButton")
        self.btn_menu_edit.setFixedSize(50, 28)
        self.btn_menu_edit.clicked.connect(self._show_edit_menu)
        title_layout.addWidget(self.btn_menu_edit)

        self.btn_menu_help = QPushButton("帮助")
        self.btn_menu_help.setObjectName("menuButton")
        self.btn_menu_help.setFixedSize(50, 28)
        self.btn_menu_help.clicked.connect(self._show_help_menu)
        title_layout.addWidget(self.btn_menu_help)

        # 编码选择
        encoding_label = QLabel("编码:")
        title_layout.addWidget(encoding_label)

        self.encoding_combo = QComboBox()
        self.encoding_combo.setFixedWidth(100)
        encodings = [
            "UTF-8",
            "GBK",
            "GB2312",
            "GB18030",
            "Big5",
            "Shift-JIS",
            "EUC-KR",
            "Latin1",
            "Windows-1252",
            "UTF-16",
            "UTF-16LE",
            "UTF-16BE",
        ]
        self.encoding_combo.addItems(encodings)
        self.encoding_combo.setCurrentText("UTF-8")
        self.encoding_combo.currentTextChanged.connect(self._on_encoding_changed)
        title_layout.addWidget(self.encoding_combo)

        # 主题选择
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["亮色", "暗色"])
        self.theme_combo.setFixedWidth(70)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        title_layout.addWidget(self.theme_combo)

        # ---------- 新增：透明度滑块 ----------
        trans_label = QLabel("透明度:")
        trans_label.setFixedWidth(45)
        title_layout.addWidget(trans_label)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setFixedWidth(70)
        self.opacity_slider.setRange(50, 100)      # 50% ~ 100%
        self.opacity_slider.setSingleStep(1)
        self.opacity_slider.setPageStep(5)
        self.opacity_slider.setValue(85)           # 默认 0.85
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        title_layout.addWidget(self.opacity_slider)

        self.opacity_label = QLabel("85%")
        self.opacity_label.setFixedWidth(40)
        title_layout.addWidget(self.opacity_label)

        title_layout.addStretch()

        # 窗口控制按钮
        self.btn_min = QPushButton("—")
        self.btn_min.setObjectName("titleMinButton")
        self.btn_min.setFixedSize(40, 34)
        self.btn_min.clicked.connect(self.showMinimized)
        title_layout.addWidget(self.btn_min)

        self.btn_max = QPushButton("□")
        self.btn_max.setObjectName("titleMaxButton")
        self.btn_max.setFixedSize(40, 34)
        self.btn_max.clicked.connect(self._toggle_maximize)
        title_layout.addWidget(self.btn_max)

        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("titleCloseButton")
        self.btn_close.setFixedSize(40, 34)
        self.btn_close.clicked.connect(self.close)
        title_layout.addWidget(self.btn_close)

        main_layout.addWidget(self.title_bar)

        # ===== 内容区域 =====
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 10, 15, 15)
        content_layout.setSpacing(10)

        # 主分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(3)
        splitter.setStyleSheet("QSplitter::handle { background: rgba(200,200,200,0.3); }")

        # ---------- 左：文件列表 ----------
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        # 工具栏按钮
        tool_bar = QHBoxLayout()
        self.btn_add_files = QPushButton("📂 添加文件")
        self.btn_add_files.clicked.connect(self.add_files)
        self.btn_add_folder = QPushButton("📁 添加文件夹")
        self.btn_add_folder.clicked.connect(self.add_folder)
        self.btn_remove_selected = QPushButton("✖ 移除选中")
        self.btn_remove_selected.setObjectName("dangerButton")
        self.btn_remove_selected.clicked.connect(self.remove_selected)
        self.btn_clear_list = QPushButton("🗑 清空列表")
        self.btn_clear_list.setObjectName("dangerButton")
        self.btn_clear_list.clicked.connect(self.clear_list)

        tool_bar.addWidget(self.btn_add_files)
        tool_bar.addWidget(self.btn_add_folder)
        tool_bar.addStretch()
        tool_bar.addWidget(self.btn_remove_selected)
        tool_bar.addWidget(self.btn_clear_list)
        left_layout.addLayout(tool_bar)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["文件名", "标题", "艺术家", "专辑", "时长"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.itemSelectionChanged.connect(self.on_file_selected)
        left_layout.addWidget(self.table)
        splitter.addWidget(left_widget)

        # ---------- 右：编辑面板 ----------
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        right_layout.setSpacing(10)

        # 标签编辑
        edit_group = QGroupBox("标签编辑")
        edit_layout = QFormLayout(edit_group)
        self.tag_inputs = {}
        common_tags = [
            ("标题", "TITLE"),
            ("艺术家", "ARTIST"),
            ("专辑", "ALBUM"),
            ("专辑艺术家", "ALBUMARTIST"),
            ("年份", "DATE"),
            ("音轨号", "TRACKNUMBER"),
            ("碟片号", "DISCNUMBER"),
            ("流派", "GENRE"),
            ("作曲家", "COMPOSER"),
            ("注释", "COMMENT"),
        ]
        for label, key in common_tags:
            le = QLineEdit()
            le.setPlaceholderText(f"输入{label}...")
            self.tag_inputs[key] = le
            edit_layout.addRow(label + ":", le)
        right_layout.addWidget(edit_group)

        # 按钮容器
        btn_container = QVBoxLayout()
        btn_container.setSpacing(6)

        # 第一行：保存相关操作
        btn_row1 = QHBoxLayout()
        self.btn_save = QPushButton("💾 保存当前")
        self.btn_save.setObjectName("saveButton")
        self.btn_save.clicked.connect(self.save_current_file)

        self.btn_save_selected = QPushButton("📋 应用到选中并保存(覆盖空白行)")
        self.btn_save_selected.setObjectName("saveButton")
        self.btn_save_selected.clicked.connect(self.save_to_selected_files)

        self.btn_apply = QPushButton("📥 应用到选中(忽略空白行)")
        self.btn_apply.clicked.connect(self.apply_to_all_selected)

        btn_row1.addWidget(self.btn_save)
        btn_row1.addWidget(self.btn_save_selected)
        btn_row1.addWidget(self.btn_apply)
        btn_row1.addStretch()

        # 第二行：批量操作和工具
        btn_row2 = QHBoxLayout()
        self.btn_save_all = QPushButton("💾 保存所有")
        self.btn_save_all.setObjectName("saveButton")
        self.btn_save_all.clicked.connect(self.save_all_files)

        self.btn_reload = QPushButton("🔄 重新加载所有")
        self.btn_reload.clicked.connect(self.reload_current_file)

        btn_row2.addWidget(self.btn_save_all)
        btn_row2.addWidget(self.btn_reload)
        btn_row2.addStretch()

        btn_container.addLayout(btn_row1)
        btn_container.addLayout(btn_row2)
        right_layout.addLayout(btn_container)

        # 文件信息
        info_group = QGroupBox("文件信息")
        info_layout = QFormLayout(info_group)
        self.lbl_path = QLabel("未选择文件")
        self.lbl_path.setWordWrap(True)
        self.lbl_path.setStyleSheet("color: #888;")
        self.lbl_format = QLabel("-")
        self.lbl_length = QLabel("-")
        info_layout.addRow("路径:", self.lbl_path)
        info_layout.addRow("格式:", self.lbl_format)
        info_layout.addRow("时长:", self.lbl_length)
        right_layout.addWidget(info_group)

        # 日志文本框
        log_group = QGroupBox("操作日志")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.log_text.setStyleSheet("font-size: 11px; background: rgba(255,255,255,0.5);")
        log_layout.addWidget(self.log_text)
        log_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(log_group)

        splitter.addWidget(right_widget)
        splitter.setSizes([550, 550])

        content_layout.addWidget(splitter, 1)
        main_layout.addWidget(content_widget)

        # 应用样式（圆角遮罩）
        self._update_mask()

    # ---------- 事件过滤器：处理标题栏双击 ----------
    def eventFilter(self, obj, event):
        if obj == self.title_bar and event.type() == QEvent.MouseButtonDblClick:
            self._toggle_maximize()
            return True
        return super().eventFilter(obj, event)

    # ---------- 窗口拖动（最大化时禁用） ----------
    def _title_mouse_press(self, e):
        if e.button() == Qt.LeftButton and not self.isMaximized():
            self.drag_pos = e.globalPos()
            self.dragging = True
            e.accept()

    def _title_mouse_move(self, e):
        if self.dragging and not self.isMaximized():
            self.move(self.pos() + e.globalPos() - self.drag_pos)
            self.drag_pos = e.globalPos()
            e.accept()

    def _title_mouse_release(self, e):
        if e.button() == Qt.LeftButton:
            self.dragging = False
            e.accept()

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.btn_max.setText("□")
        else:
            self.showMaximized()
            self.btn_max.setText("❐")
        QTimer.singleShot(10, self._update_mask)

    def _update_mask(self):
        rect = self.rect()
        if rect.width() <= 0 or rect.height() <= 0:
            return
        path = QPainterPath()
        radius = 8
        path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), radius, radius)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._update_mask()

    # ---------- 主题 ----------
    def _on_theme_changed(self, idx):
        theme = 'dark' if idx == 1 else 'light'
        self.current_theme = theme
        self._apply_theme(theme)
        self.save_settings()

    def _apply_theme(self, theme_name):
        self.current_theme = theme_name
        stylesheet = get_global_stylesheet(theme_name, self.bg_opacity)
        QApplication.instance().setStyleSheet(stylesheet)
        # 更新组合框显示（不触发信号）
        idx = 0 if theme_name == 'light' else 1
        if self.theme_combo.currentIndex() != idx:
            self.theme_combo.blockSignals(True)
            self.theme_combo.setCurrentIndex(idx)
            self.theme_combo.blockSignals(False)

    # ---------- 透明度 ----------
    def _on_opacity_changed(self, value):
        self.bg_opacity = value / 100.0
        self.opacity_label.setText(f"{value}%")
        # 重新应用样式（保持当前主题）
        self._apply_theme(self.current_theme)
        self.save_settings()

    # ---------- 编码切换 ----------
    def _on_encoding_changed(self, encoding: str):
        self.current_encoding = encoding
        self.log_text.append(f"📝 编码已切换为: {encoding}，请重新加载文件以生效")
        self.status_label.setText(f"编码: {encoding}，请重新加载文件")
        self.save_settings()

    # ---------- 菜单栏 ----------
    def _setup_actions(self):
        self.act_add_files = QAction("添加文件", self)
        self.act_add_files.triggered.connect(self.add_files)
        self.act_add_folder = QAction("添加文件夹", self)
        self.act_add_folder.triggered.connect(self.add_folder)
        self.act_clear = QAction("清空列表", self)
        self.act_clear.triggered.connect(self.clear_list)
        self.act_exit = QAction("退出", self)
        self.act_exit.triggered.connect(self.close)

        self.act_save = QAction("保存当前", self)
        self.act_save.triggered.connect(self.save_current_file)
        self.act_save_all = QAction("保存所有", self)
        self.act_save_all.triggered.connect(self.save_all_files)

        self.act_about = QAction("关于", self)
        self.act_about.triggered.connect(self.show_about)

    def _setup_statusbar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.status_label = QLabel("就绪 | 支持 MP3, FLAC, OGG, M4A, WMA, OPUS, WAV")
        self.statusBar.addWidget(self.status_label)

    def _show_file_menu(self):
        menu = QMenu(self)
        menu.addAction(self.act_add_files)
        menu.addAction(self.act_add_folder)
        menu.addSeparator()
        menu.addAction(self.act_clear)
        menu.addSeparator()
        menu.addAction(self.act_exit)
        menu.exec_(self.btn_menu_file.mapToGlobal(self.btn_menu_file.rect().bottomLeft()))

    def _show_edit_menu(self):
        menu = QMenu(self)
        menu.addAction(self.act_save)
        menu.addAction(self.act_save_all)
        menu.exec_(self.btn_menu_edit.mapToGlobal(self.btn_menu_edit.rect().bottomLeft()))

    def _show_help_menu(self):
        menu = QMenu(self)
        menu.addAction(self.act_about)
        menu.exec_(self.btn_menu_help.mapToGlobal(self.btn_menu_help.rect().bottomLeft()))

    # ---------- 文件操作 ----------
    def add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "选择音频文件", "",
            "音频文件 (*.mp3 *.flac *.ogg *.m4a *.wma *.opus *.wav);;所有文件 (*.*)"
        )
        if paths:
            self.load_files(paths)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            extensions = {'.mp3', '.flac', '.ogg', '.m4a', '.wma', '.opus', '.wav'}
            audio_files = []
            for ext in extensions:
                audio_files.extend(Path(folder).rglob(f"*{ext}"))
                audio_files.extend(Path(folder).rglob(f"*{ext.upper()}"))
            paths = list(set(str(f) for f in audio_files))
            if paths:
                self.load_files(paths)
            else:
                QMessageBox.information(self, "提示", "该文件夹中没有找到支持的音频文件")

    def load_files(self, file_paths):
        if self.is_loading:
            QMessageBox.warning(self, "提示", "正在加载中，请稍候...")
            return
        existing = set(self.files_data.keys())
        new_files = [f for f in file_paths if f not in existing]
        if not new_files:
            QMessageBox.information(self, "提示", "所有文件已在列表中")
            return

        self.is_loading = True
        self.status_label.setText(f"正在加载 {len(new_files)} 个文件... (编码: {self.current_encoding})")

        progress = QProgressDialog("正在读取文件标签...", "取消", 0, len(new_files), self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.canceled.connect(self._cancel_loading)

        self.load_thread = LoadFilesThread(new_files, self.current_encoding)
        self.load_thread.progress.connect(lambda cur, total: progress.setValue(cur))
        self.load_thread.file_loaded.connect(self._add_file_to_table)
        self.load_thread.error.connect(self.log_text.append)
        self.load_thread.finished.connect(lambda: self._on_load_finished(progress))
        self.load_thread.start()

    def _cancel_loading(self):
        if self.load_thread:
            self.load_thread.cancel()

    def _on_load_finished(self, progress):
        self.is_loading = False
        progress.close()
        self.status_label.setText(f"就绪 | 共 {self.table.rowCount()} 个文件")
        self.log_text.append(f"✅ 加载完成，共 {self.table.rowCount()} 个文件 (编码: {self.current_encoding})")
        self.load_thread = None

    def _add_file_to_table(self, file_path, tags, length):
        self.files_data[file_path] = {"tags": tags, "length": length}
        row = self.table.rowCount()
        self.table.insertRow(row)

        name_item = QTableWidgetItem(os.path.basename(file_path))
        name_item.setToolTip(file_path)
        name_item.setData(Qt.UserRole, file_path)
        self.table.setItem(row, 0, name_item)

        title = tags.get("TITLE", [""])[0] or ""
        self.table.setItem(row, 1, QTableWidgetItem(title))
        self.table.setItem(row, 2, QTableWidgetItem(tags.get("ARTIST", [""])[0] or ""))
        self.table.setItem(row, 3, QTableWidgetItem(tags.get("ALBUM", [""])[0] or ""))

        if length > 0:
            m, s = divmod(length, 60)
            length_str = f"{m}:{s:02d}"
        else:
            length_str = "--:--"
        self.table.setItem(row, 4, QTableWidgetItem(length_str))

    def clear_list(self):
        if self.table.rowCount() == 0:
            return
        reply = QMessageBox.question(self, "确认清空", "确定要清空所有文件吗？未保存的更改将丢失。",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.table.setRowCount(0)
            self.files_data.clear()
            self.current_file = None
            self._clear_tag_inputs()
            self.lbl_path.setText("未选择文件")
            self.lbl_format.setText("-")
            self.lbl_length.setText("-")
            self.status_label.setText("就绪 | 列表已清空")

    def remove_selected(self):
        rows = set()
        for item in self.table.selectedItems():
            rows.add(item.row())
        if not rows:
            return
        reply = QMessageBox.question(self, "确认移除", f"确定要移除选中的 {len(rows)} 个文件吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            for row in sorted(rows, reverse=True):
                file_path = self.table.item(row, 0).data(Qt.UserRole)
                if file_path in self.files_data:
                    del self.files_data[file_path]
                self.table.removeRow(row)
            self.current_file = None
            self._clear_tag_inputs()
            self.lbl_path.setText("未选择文件")
            self.lbl_format.setText("-")
            self.lbl_length.setText("-")
            self.status_label.setText(f"就绪 | 共 {self.table.rowCount()} 个文件")

    # ---------- 选中与显示 ----------
    def on_file_selected(self):
        items = self.table.selectedItems()
        if not items:
            return
        row = items[0].row()
        file_path = self.table.item(row, 0).data(Qt.UserRole)
        if not file_path or file_path not in self.files_data:
            return
        self.current_file = file_path
        data = self.files_data[file_path]
        tags = data.get("tags", {})
        length = data.get("length", 0)

        self.lbl_path.setText(file_path)
        ext = os.path.splitext(file_path)[1].upper()
        self.lbl_format.setText(ext)
        if length > 0:
            m, s = divmod(length, 60)
            self.lbl_length.setText(f"{m}:{s:02d}")
        else:
            self.lbl_length.setText("--:--")

        for key, le in self.tag_inputs.items():
            vals = tags.get(key, [])
            le.setText(vals[0] if vals else "")

    def _clear_tag_inputs(self):
        for le in self.tag_inputs.values():
            le.setText("")

    # ---------- 保存核心 ----------
    def _save_tags_to_file(self, file_path, new_tags):
        try:
            if self.current_encoding and self.current_encoding != 'UTF-8':
                new_tags = encode_tags_for_save(new_tags, self.current_encoding)

            with taglib.File(file_path, save_on_exit=True) as song:
                for key, values in new_tags.items():
                    song.tags[key] = values
                for key in list(song.tags.keys()):
                    if key not in new_tags:
                        del song.tags[key]
            if self.current_encoding and self.current_encoding != 'UTF-8':
                new_tags = decode_tags(new_tags, self.current_encoding)
            self.files_data[file_path]["tags"] = new_tags
            self._update_table_row(file_path)
            return True, None
        except Exception as e:
            err = str(e)
            self.log_text.append(f"❌ 保存失败: {os.path.basename(file_path)} - {err}")
            return False, err

    def _update_table_row(self, file_path):
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).data(Qt.UserRole) == file_path:
                data = self.files_data.get(file_path, {})
                tags = data.get("tags", {})
                self.table.item(row, 1).setText(tags.get("TITLE", [""])[0] or "")
                self.table.item(row, 2).setText(tags.get("ARTIST", [""])[0] or "")
                self.table.item(row, 3).setText(tags.get("ALBUM", [""])[0] or "")
                break

    # ---------- 保存操作 ----------
    def save_current_file(self):
        if not self.current_file:
            QMessageBox.warning(self, "提示", "请先选择一个文件")
            return
        new_tags = self._collect_ui_tags()
        success, _ = self._save_tags_to_file(self.current_file, new_tags)
        if success:
            self.log_text.append(f"💾 已保存当前文件: {os.path.basename(self.current_file)} (编码: {self.current_encoding})")
            self.status_label.setText(f"已保存: {os.path.basename(self.current_file)}")

    def save_to_selected_files(self):
        rows = set()
        for item in self.table.selectedItems():
            rows.add(item.row())
        if not rows:
            QMessageBox.warning(self, "提示", "请先选择要保存的文件")
            return
        new_tags = self._collect_ui_tags()
        if not new_tags:
            QMessageBox.warning(self, "提示", "没有可保存的标签内容")
            return

        reply = QMessageBox.question(self, "确认保存",
                                     f"将当前标签保存到选中的 {len(rows)} 个文件？（空字段将删除）",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        success_count = 0
        for row in rows:
            file_path = self.table.item(row, 0).data(Qt.UserRole)
            if file_path and file_path in self.files_data:
                ok, _ = self._save_tags_to_file(file_path, new_tags)
                if ok:
                    success_count += 1
        self.log_text.append(f"📋 已保存 {success_count} 个选中文件 (编码: {self.current_encoding})")
        self.status_label.setText(f"已保存 {success_count} 个选中文件")

    def apply_to_all_selected(self):
        rows = set()
        for item in self.table.selectedItems():
            rows.add(item.row())
        if not rows:
            QMessageBox.warning(self, "提示", "请先选择要应用的文件")
            return
        new_tags = self._collect_ui_tags()
        if not new_tags:
            QMessageBox.warning(self, "提示", "没有可应用的标签内容")
            return

        for row in rows:
            file_path = self.table.item(row, 0).data(Qt.UserRole)
            if file_path and file_path in self.files_data:
                old_tags = self.files_data[file_path]["tags"]
                for key, vals in new_tags.items():
                    old_tags[key] = vals
                self._update_table_row(file_path)
        self.log_text.append(f"📥 已暂存到 {len(rows)} 个文件（未保存到磁盘）")
        self.status_label.setText(f"已暂存 {len(rows)} 个文件")

    def save_all_files(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "提示", "列表为空")
            return
        reply = QMessageBox.question(self, "确认保存",
                                     f"确定要将内存中的所有更改写入磁盘吗？（{self.table.rowCount()} 个文件）",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        success = 0
        fail = 0
        for row in range(self.table.rowCount()):
            file_path = self.table.item(row, 0).data(Qt.UserRole)
            if file_path and file_path in self.files_data:
                tags = self.files_data[file_path].get("tags", {})
                try:
                    if self.current_encoding and self.current_encoding != 'UTF-8':
                        tags_to_write = encode_tags_for_save(tags, self.current_encoding)
                    else:
                        tags_to_write = tags
                    with taglib.File(file_path, save_on_exit=True) as song:
                        for key, values in tags_to_write.items():
                            song.tags[key] = values
                        for key in list(song.tags.keys()):
                            if key not in tags_to_write:
                                del song.tags[key]
                    success += 1
                except Exception as e:
                    fail += 1
                    self.log_text.append(f"❌ 保存失败: {os.path.basename(file_path)} - {str(e)}")
        self.log_text.append(f"💾 全部落盘完成: 成功 {success} 个，失败 {fail} 个 (编码: {self.current_encoding})")
        self.status_label.setText(f"全部保存完成: 成功 {success} 个")

    def _collect_ui_tags(self):
        new_tags = {}
        for key, le in self.tag_inputs.items():
            text = le.text().strip()
            if text:
                new_tags[key] = [text]
        return new_tags

    def reload_current_file(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "提示", "列表为空，无需刷新")
            return

        current_selected = self.current_file

        for row in range(self.table.rowCount()):
            file_path = self.table.item(row, 0).data(Qt.UserRole)
            if not file_path or file_path not in self.files_data:
                continue
            try:
                with taglib.File(file_path) as song:
                    tags = dict(song.tags)
                    if self.current_encoding and self.current_encoding != 'UTF-8':
                        tags = decode_tags(tags, self.current_encoding)
                    length = int(song.length) if song.length is not None else 0
                    self.files_data[file_path] = {"tags": tags, "length": length}
                    self.table.item(row, 1).setText(tags.get("TITLE", [""])[0] or "")
                    self.table.item(row, 2).setText(tags.get("ARTIST", [""])[0] or "")
                    self.table.item(row, 3).setText(tags.get("ALBUM", [""])[0] or "")
                    if length > 0:
                        m, s = divmod(length, 60)
                        self.table.item(row, 4).setText(f"{m}:{s:02d}")
                    else:
                        self.table.item(row, 4).setText("--:--")
            except Exception as e:
                self.log_text.append(f"❌ 刷新失败: {os.path.basename(file_path)} - {str(e)}")

        if current_selected and current_selected in self.files_data:
            for row in range(self.table.rowCount()):
                if self.table.item(row, 0).data(Qt.UserRole) == current_selected:
                    self.table.selectRow(row)
                    self.on_file_selected()
                    break
        else:
            self.current_file = None
            self._clear_tag_inputs()
            self.lbl_path.setText("未选择文件")
            self.lbl_format.setText("-")
            self.lbl_length.setText("-")

        self.log_text.append(f"🔄 已刷新所有文件（{self.table.rowCount()} 个），编码: {self.current_encoding}")
        self.status_label.setText(f"已刷新所有文件")

    # ---------- 关于 ----------
    def show_about(self):
        QMessageBox.about(
            self,
            "关于音乐标签编辑器",
            "<h2>📝 音乐标签编辑器</h2>"
            "<p>基于 PyQt5 + pytaglib 开发</p>"
            "<p><b>支持格式：</b>MP3, FLAC, OGG, M4A, WMA, OPUS, WAV</p>"
            "</ul>"
            "<p style='color:#888;'>版本 3.1.0</p>"
            "<p style='color:#888;'>Made by cYy</p>"
        )

    # ---------- 窗口关闭 ----------
    def closeEvent(self, e):
        if self.table.rowCount() > 0:
            reply = QMessageBox.question(self, "确认退出", "确定要退出吗？",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                if self.load_thread and self.load_thread.isRunning():
                    self.load_thread.cancel()
                    self.load_thread.wait()
                self.save_settings()
                e.accept()
            else:
                e.ignore()
        else:
            self.save_settings()
            e.accept()


# ==================== 启动 ====================
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("音乐标签编辑器")
    font = QFont()
    font.setFamily("Microsoft YaHei, PingFang SC, Helvetica Neue, Segoe UI, sans-serif")
    font.setPointSize(9)
    app.setFont(font)

    app.setStyleSheet(get_global_stylesheet('light', 0.85))
    window = MusicTagEditor()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
