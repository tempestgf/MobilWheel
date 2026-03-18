import os
import sys
import threading
import logging
from io import StringIO
from pathlib import Path

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel,
                             QProgressBar, QTextEdit, QGridLayout, QCheckBox,
                             QGraphicsDropShadowEffect, QFrame, QSizePolicy,
                             QMessageBox)
from PyQt5.QtCore import pyqtSignal, QObject, QTimer, Qt, QSettings
from PyQt5.QtGui import QIcon, QFont, QColor, QTextCursor, QPixmap, QPainter, QPainterPath, QFontDatabase, QLinearGradient, QPen, QBrush

# Configurar logging
log_stream = StringIO()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', stream=log_stream)

import xbox as server_module
from app_version import APP_VERSION
from updater import AppUpdater, UpdateError
from vjoy_bootstrap import check_and_setup_vjoy

try:
    from game_telemetry import GameTelemetryReader, GamePhysics
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False
    logging.warning("Game Telemetry module not available")

# Signals class for thread-safe UI updates
class WorkerSignals(QObject):
    update_axis = pyqtSignal(str, int)
    toggle_button = pyqtSignal(str)
    log_update = pyqtSignal(str)
    telemetry_update = pyqtSignal(object)

# ── Racing stripe header widget ────────────────────────────────────────────
class AccentStripe(QWidget):
    """Decorative horizontal accent stripe with a sleek gradient."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(3)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0.0,  QColor("#EA580C")) # Tailwind orange-600
        grad.setColorAt(0.5,  QColor("#F97316")) # Tailwind orange-500
        grad.setColorAt(1.0,  QColor("#EA580C"))
        painter.fillRect(self.rect(), QBrush(grad))


class ModernGaugeBar(QProgressBar):
    """Custom progress bar with a clean, professional look."""
    def __init__(self, max_val=100, accent="#F97316", parent=None):
        super().__init__(parent)
        self.setMaximum(max_val)
        self.setTextVisible(False)
        self._accent = QColor(accent)
        self.setFixedHeight(12)
        # We fully paint our own background — skip Qt's redundant fill
        self.setAttribute(Qt.WA_OpaquePaintEvent)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        radius = r.height() / 2.0

        # Track
        path_bg = QPainterPath()
        path_bg.addRoundedRect(r.x(), r.y(), r.width(), r.height(), radius, radius)
        painter.fillPath(path_bg, QColor("#262626")) # Tailwind neutral-800
        painter.setPen(Qt.NoPen)

        # Fill
        ratio = self.value() / max(self.maximum(), 1)
        fill_w = int(r.width() * ratio)
        if fill_w > 2:
            fill_path = QPainterPath()
            fill_path.addRoundedRect(r.x(), r.y(), fill_w, r.height(), radius, radius)
            painter.fillPath(fill_path, QBrush(self._accent))


class ServerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mobile Wheel Server - Geneon Edition")
        self.setMinimumSize(720, 640)
        self.resize(840, 820)
        
        # Base path
        self.base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(self.base_path, "app_logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
            # Set taskbar icon on Windows
            if sys.platform == 'win32':
                import ctypes
                myappid = 'geneon.mobilwheel.server.1' # arbitrary string
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.signals = WorkerSignals()
        self.signals.update_axis.connect(self.update_progress_bars)
        self.signals.toggle_button.connect(self.toggle_button_check)
        self.signals.log_update.connect(self.append_log)
        self.signals.telemetry_update.connect(self.update_telemetry_ui)

        self.server_thread = None
        self.server_running = threading.Event()
        self.update_in_progress = False
        self.updater = AppUpdater(current_version=APP_VERSION)
        self.update_check_timer = QTimer(self)
        self.update_check_timer.timeout.connect(self.check_updates_silent)

        self.telemetry_reader = None
        self.telemetry_connected = False
        self.telemetry_auto_detect_active = False

        self.settings = QSettings("Geneon", "MobilWheelServer")

        # Load Custom Font
        font_path = os.path.join(self.base_path, "museo_moderno.ttf")
        self.museo_font_family = "Segoe UI" # Fallback
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                self.museo_font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        self.init_ui()
        self.apply_stylesheet()

        # Log timer
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.poll_logs)
        self.log_timer.start(100)

        if TELEMETRY_AVAILABLE:
            self.start_telemetry_auto_detect()

        # Check and setup vJoy if needed
        QTimer.singleShot(100, lambda: check_and_setup_vjoy(self, only_check=False))

        # Auto-start server if setting is enabled
        if self.settings.value("auto_start_server", False, type=bool):
            QTimer.singleShot(500, self.start_server)

        # Auto-check updates after UI is responsive
        if self.settings.value("auto_check_updates", True, type=bool):
            QTimer.singleShot(1800, self.check_updates_silent)
            # Re-check every 12 hours
            self.update_check_timer.start(12 * 60 * 60 * 1000)

    def _make_shadow(self, blur=15, color=QColor(0, 0, 0, 100), offset=(0, 2)):
        s = QGraphicsDropShadowEffect()
        s.setBlurRadius(blur)
        s.setColor(color)
        s.setOffset(*offset)
        return s

    def _section_label(self, text):
        """Small gray uppercase section divider label."""
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 8, QFont.DemiBold))
        lbl.setStyleSheet(
            "color: #9E9E9E;"
            "letter-spacing: 2px;"
            "margin-top: 10px;"
            "margin-bottom: 2px;"
        )
        return lbl

    def _value_label(self, text, size=20):
        lbl = QLabel(text)
        lbl.setFont(QFont("Consolas", size, QFont.Bold))
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color: #FFFFFF;")
        return lbl

    def _make_stat_card(self, title, value_widget):
        """Mini card widget with a title and a value widget inside."""
        card = QFrame()
        card.setObjectName("StatCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)
        t = QLabel(title)
        t.setFont(QFont("Segoe UI", 7, QFont.DemiBold))
        t.setAlignment(Qt.AlignCenter)
        t.setStyleSheet("color: #8E8E8E; letter-spacing: 1px;")
        layout.addWidget(t)
        layout.addWidget(value_widget)
        return card

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("ContentWidget")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ── Top accent stripe ─────────────────────────────────────────────
        main_layout.addWidget(AccentStripe())

        # ── Inner content (NO scroll — responsive direct layout) ──────────
        inner = QVBoxLayout()
        inner.setSpacing(10)
        inner.setContentsMargins(32, 16, 32, 16)
        main_layout.addLayout(inner, stretch=1)

        # ── HEADER ───────────────────────────────────────────────────────
        header_layout = QHBoxLayout()
        header_layout.setSpacing(0)

        logo_label = QLabel()
        logo_path = os.path.join(self.base_path, "app_logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setGraphicsEffect(self._make_shadow(20, QColor(249, 115, 22, 60), (0, 0))) # orange shadow

        title_layout = QVBoxLayout()
        title_layout.setSpacing(1)
        title_layout.setContentsMargins(14, 0, 0, 0)
        title_label = QLabel("GENEON")
        title_label.setFont(QFont(self.museo_font_family, 26, QFont.Bold))
        title_label.setStyleSheet("color: #FAFAFA; letter-spacing: 2px;")
        subtitle_label = QLabel("MOBILE WHEEL SERVER")
        subtitle_label.setFont(QFont("Segoe UI", 9, QFont.Medium))
        subtitle_label.setStyleSheet("color: #F97316; letter-spacing: 5px;") # orange-500
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)

        header_layout.addWidget(logo_label, alignment=Qt.AlignVCenter)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Right column: status pill + settings checkboxes (embedded in header)
        right_col = QVBoxLayout()
        right_col.setSpacing(6)
        right_col.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        self.status_pill = QLabel("  ●  OFFLINE  ")
        self.status_pill.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self.status_pill.setAlignment(Qt.AlignCenter)
        self.status_pill.setStyleSheet(
            "color: #F97316; background-color: transparent;" # Orange
            "border: 1px solid #F97316; border-radius: 6px;"
            "padding: 3px 12px; letter-spacing: 2px;"
        )
        self.status_indicator = self.status_pill  # compat

        cb_row = QHBoxLayout()
        cb_row.setSpacing(18)
        self.autostart_app_cb = QCheckBox("Startup")
        self.autostart_app_cb.setChecked(self.check_autostart())
        self.autostart_app_cb.stateChanged.connect(self.toggle_autostart)
        self.autostart_server_cb = QCheckBox("Auto-start")
        self.autostart_server_cb.setChecked(self.settings.value("auto_start_server", False, type=bool))
        self.autostart_server_cb.stateChanged.connect(
            lambda state: self.settings.setValue("auto_start_server", state == Qt.Checked)
        )
        self.auto_update_cb = QCheckBox("Auto-update")
        self.auto_update_cb.setChecked(self.settings.value("auto_check_updates", True, type=bool))
        self.auto_update_cb.stateChanged.connect(
            lambda state: self.settings.setValue("auto_check_updates", state == Qt.Checked)
        )
        cb_row.addWidget(self.autostart_app_cb)
        cb_row.addWidget(self.autostart_server_cb)
        cb_row.addWidget(self.auto_update_cb)

        right_col.addWidget(self.status_pill, alignment=Qt.AlignRight)
        right_col.addLayout(cb_row)
        header_layout.addLayout(right_col)
        inner.addLayout(header_layout)

        # ── Racing stripe divider ─────────────────────────────────────────
        inner.addWidget(AccentStripe())

        # ── CONTROL BUTTONS ───────────────────────────────────────────────
        control_layout = QHBoxLayout()
        control_layout.setSpacing(12)

        self.start_btn = QPushButton("▶  START")
        self.start_btn.setObjectName("StartBtn")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setMinimumHeight(44)
        self.start_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.start_btn.clicked.connect(self.start_server)

        self.stop_btn = QPushButton("■  STOP")
        self.stop_btn.setObjectName("StopBtn")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setMinimumHeight(44)
        self.stop_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.stop_btn.clicked.connect(self.stop_server)
        self.stop_btn.setEnabled(False)

        self.restart_btn = QPushButton("↺  RESTART")
        self.restart_btn.setObjectName("RestartBtn")
        self.restart_btn.setCursor(Qt.PointingHandCursor)
        self.restart_btn.setMinimumHeight(44)
        self.restart_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.restart_btn.clicked.connect(self.restart_server)
        self.restart_btn.setEnabled(False)

        self.update_btn = QPushButton("⬇  UPDATE")
        self.update_btn.setObjectName("UpdateBtn")
        self.update_btn.setCursor(Qt.PointingHandCursor)
        self.update_btn.setMinimumHeight(44)
        self.update_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.update_btn.clicked.connect(self.check_updates_manual)

        self.start_btn.setGraphicsEffect(self._make_shadow(15, QColor(249, 115, 22, 40), (0, 2))) # orange shadow
        control_layout.addWidget(self.start_btn, 2)
        control_layout.addWidget(self.stop_btn, 1)
        control_layout.addWidget(self.restart_btn, 1)
        control_layout.addWidget(self.update_btn, 1)
        inner.addLayout(control_layout)

        # ── TELEMETRY ─────────────────────────────────────────────────────
        if TELEMETRY_AVAILABLE:
            inner.addWidget(self._section_label("GAME TELEMETRY"))

            tele_frame = QFrame()
            tele_frame.setObjectName("TelemetryFrame")
            tele_grid = QGridLayout(tele_frame)
            tele_grid.setContentsMargins(16, 10, 16, 10)
            tele_grid.setSpacing(7)

            # Row 0 — status + disconnect
            self.telemetry_status_lbl = QLabel("●  Searching for game...")
            self.telemetry_status_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.telemetry_status_lbl.setStyleSheet("color: #F59E0B;") # Amber-500
            self.telemetry_disconnect_btn = QPushButton("DISCONNECT")
            self.telemetry_disconnect_btn.setObjectName("DisconnectBtn")
            self.telemetry_disconnect_btn.setEnabled(False)
            self.telemetry_disconnect_btn.clicked.connect(self.disconnect_telemetry)
            self.telemetry_disconnect_btn.setFixedHeight(28)
            self.telemetry_disconnect_btn.setFixedWidth(114)
            self.telemetry_disconnect_btn.setFont(QFont("Segoe UI", 8, QFont.Bold))
            tele_grid.addWidget(self.telemetry_status_lbl, 0, 0, 1, 3)
            tele_grid.addWidget(self.telemetry_disconnect_btn, 0, 3, 1, 1, Qt.AlignRight)

            # Row 1 — stat cards: Speed | Gear | RPM
            self.telemetry_speed_val = self._value_label("---", 18)
            self.telemetry_gear_val  = self._value_label("-",   18)
            self.telemetry_rpm_val   = self._value_label("0",   16)
            self.telemetry_rpm_lbl   = self.telemetry_rpm_val   # compat
            speed_card = self._make_stat_card("SPEED  km/h", self.telemetry_speed_val)
            gear_card  = self._make_stat_card("GEAR",        self.telemetry_gear_val)
            rpm_card   = self._make_stat_card("RPM",         self.telemetry_rpm_val)
            tele_grid.addWidget(speed_card, 1, 0, 1, 2)
            tele_grid.addWidget(gear_card,  1, 2, 1, 1)
            tele_grid.addWidget(rpm_card,   1, 3, 1, 1)

            # Row 2 — RPM bar
            self.telemetry_rpm_bar = ModernGaugeBar(8000, "#F97316") # Orange-500
            tele_grid.addWidget(self.telemetry_rpm_bar, 2, 0, 1, 4)

            # Row 3 — Gas bar
            gas_lbl = QLabel("GAS")
            gas_lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
            gas_lbl.setStyleSheet("color: #FFFFFF; letter-spacing: 2px;") # White
            gas_lbl.setFixedWidth(40)
            self.telemetry_gas_bar = ModernGaugeBar(100, "#FAFAFA") # Neutral-50
            self.telemetry_gas_lbl = QLabel("0%")
            self.telemetry_gas_lbl.setFont(QFont("Consolas", 10, QFont.Bold))
            self.telemetry_gas_lbl.setStyleSheet("color: #FFFFFF;")
            self.telemetry_gas_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.telemetry_gas_lbl.setFixedWidth(38)
            tele_grid.addWidget(gas_lbl,                  3, 0)
            tele_grid.addWidget(self.telemetry_gas_bar,   3, 1, 1, 2)
            tele_grid.addWidget(self.telemetry_gas_lbl,   3, 3)

            # Row 4 — Brake bar
            brk_lbl = QLabel("BRAKE")
            brk_lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
            brk_lbl.setStyleSheet("color: #F97316; letter-spacing: 2px;") # Orange-500
            brk_lbl.setFixedWidth(40)
            self.telemetry_brake_bar = ModernGaugeBar(100, "#F97316") # Orange-500
            self.telemetry_brake_lbl = QLabel("0%")
            self.telemetry_brake_lbl.setFont(QFont("Consolas", 10, QFont.Bold))
            self.telemetry_brake_lbl.setStyleSheet("color: #F97316;")
            self.telemetry_brake_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.telemetry_brake_lbl.setFixedWidth(38)
            tele_grid.addWidget(brk_lbl,                  4, 0)
            tele_grid.addWidget(self.telemetry_brake_bar, 4, 1, 1, 2)
            tele_grid.addWidget(self.telemetry_brake_lbl, 4, 3)

            tele_grid.setColumnStretch(0, 0)
            tele_grid.setColumnStretch(1, 3)
            tele_grid.setColumnStretch(2, 1)
            tele_grid.setColumnStretch(3, 0)
            inner.addWidget(tele_frame)

        # ── AXIS INPUTS ───────────────────────────────────────────────────
        inner.addWidget(self._section_label("AXIS INPUTS"))

        axis_frame = QFrame()
        axis_frame.setObjectName("AxisFrame")
        axis_outer = QVBoxLayout(axis_frame)
        axis_outer.setContentsMargins(16, 10, 16, 10)
        axis_outer.setSpacing(9)

        def axis_row(label_text, bar_widget, accent_color):
            row = QHBoxLayout()
            row.setSpacing(12)
            lbl = QLabel(label_text)
            lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
            lbl.setStyleSheet(f"color: {accent_color}; min-width: 82px; letter-spacing: 1px;")
            row.addWidget(lbl)
            row.addWidget(bar_widget, 1)
            return row

        self.accel_bar = ModernGaugeBar(100,   "#FAFAFA") # White/Neutral-50
        self.brake_bar = ModernGaugeBar(100,   "#F97316") # Orange-500
        self.steer_bar = ModernGaugeBar(32767, "#FB923C") # Orange-400
        axis_outer.addLayout(axis_row("ACCELERATE", self.accel_bar, "#FAFAFA"))
        axis_outer.addLayout(axis_row("BRAKE",      self.brake_bar, "#F97316"))
        axis_outer.addLayout(axis_row("STEERING",   self.steer_bar, "#FB923C"))
        inner.addWidget(axis_frame)

        # ── BUTTON STATES ─────────────────────────────────────────────────
        inner.addWidget(self._section_label("BUTTON STATES"))

        btn_frame = QFrame()
        btn_frame.setObjectName("BtnFrame")
        btn_outer = QGridLayout(btn_frame)
        btn_outer.setContentsMargins(16, 8, 16, 8)
        btn_outer.setSpacing(10)
        self.buttons = {}
        btn_names = ['left_top', 'right_top', 'left_bottom', 'right_bottom', 'volume_up', 'volume_down']
        labels    = ['Left Top', 'Right Top', 'Left Bottom', 'Right Bottom', 'Vol +', 'Vol −']
        for i, (name, label) in enumerate(zip(btn_names, labels)):
            cb = QCheckBox(label)
            cb.setFont(QFont("Segoe UI", 9, QFont.Bold))
            cb.setAttribute(Qt.WA_TransparentForMouseEvents)
            cb.setFocusPolicy(Qt.NoFocus)
            self.buttons[name] = cb
            btn_outer.addWidget(cb, i // 3, i % 3)
        inner.addWidget(btn_frame)

        # ── LOG AREA — takes all remaining vertical space ─────────────────
        inner.addWidget(self._section_label("SERVER LOGS"))
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Consolas", 9))
        self.log_area.setMinimumHeight(60)
        self.log_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        inner.addWidget(self.log_area, stretch=1)

    def apply_stylesheet(self):
        qss = """
        /* ── Base ─────────────────────────────────────────────────── */
        QMainWindow {
            background-color: #0A0A0A;
        }
        QWidget {
            color: #FAFAFA;
            font-family: 'Segoe UI', sans-serif;
            background-color: transparent;
        }
        #ContentWidget {
            background-color: #0A0A0A;
        }

        /* ── Section frames (Telemetry / Axis / Buttons) ─────────── */
        #TelemetryFrame, #AxisFrame, #BtnFrame {
            background-color: #171717;
            border: 1px solid #262626;
            border-radius: 8px;
        }
        /* Left accent bar on each section frame */
        #TelemetryFrame { border-left: 4px solid #F97316; } /* Orange */
        #AxisFrame { border-left: 4px solid #FAFAFA; } /* White */
        #BtnFrame { border-left: 4px solid #525252; } /* Gray */

        /* ── Stat cards ──────────────────────────────────────────── */
        #StatCard {
            background-color: #0A0A0A;
            border: 1px solid #262626;
            border-radius: 6px;
        }

        /* ── Buttons ─────────────────────────────────────────────── */
        QPushButton {
            background-color: #171717;
            border: 1px solid #404040;
            color: #A3A3A3;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 12px;
            letter-spacing: 2px;
        }
        QPushButton:hover {
            background-color: #262626;
            border: 1px solid #F97316;
            color: #FAFAFA;
        }
        QPushButton:pressed {
            background-color: #F97316;
            color: #0A0A0A;
            border: 1px solid #F97316;
        }
        QPushButton:disabled {
            border: 1px solid #262626;
            color: #525252;
            background-color: #171717;
        }
        /* START button — highlighted */
        #StartBtn {
            background-color: #171717;
            border: 1px solid #EA580C;
            color: #F97316;
        }
        #StartBtn:hover {
            background-color: #F97316;
            border: 1px solid #F97316;
            color: #0A0A0A;
        }
        #StartBtn:disabled {
            background-color: #171717;
            border: 1px solid #262626;
            color: #525252;
        }
        /* Disconnect button */
        #DisconnectBtn {
            border: 1px solid #737373;
            color: #A3A3A3;
            background-color: transparent;
            font-size: 10px;
            letter-spacing: 1px;
            border-radius: 4px;
        }
        #DisconnectBtn:hover {
            background-color: #F97316;
            color: #0A0A0A;
            border: 1px solid #F97316;
        }
        #DisconnectBtn:disabled {
            border: 1px solid #262626;
            color: #525252;
            background-color: #171717;
        }

        /* ── Checkboxes ──────────────────────────────────────────── */
        QCheckBox {
            spacing: 8px;
            color: #A3A3A3;
            font-size: 11px;
            font-weight: 500;
        }
        QCheckBox:hover { color: #FAFAFA; }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 1px solid #525252;
            background-color: #171717;
        }
        QCheckBox::indicator:hover  { border: 1px solid #F97316; }
        QCheckBox::indicator:checked {
            background-color: #F97316;
            border: 1px solid #F97316;
            image: none;
        }

        /* ── Log area ────────────────────────────────────────────── */
        QTextEdit {
            background-color: #171717;
            border: 1px solid #262626;
            border-radius: 6px;
            padding: 10px;
            color: #D4D4D4;
            font-size: 11px;
            selection-background-color: #F97316;
            selection-color: #0A0A0A;
        }

        /* ── Scrollbars ──────────────────────────────────────────── */
        QScrollBar:vertical {
            border: none;
            background: #0A0A0A;
            width: 8px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical {
            background: #404040;
            min-height: 30px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical:hover { background: #525252; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none; background: none;
        }
        QScrollBar:horizontal { height: 0px; }
        """
        self.setStyleSheet(qss)

    def check_updates_silent(self):
        self._check_for_updates(interactive=False)

    def check_updates_manual(self):
        self._check_for_updates(interactive=True)

    def _check_for_updates(self, interactive: bool):
        if self.update_in_progress:
            return

        if interactive:
            self.update_btn.setEnabled(False)
            self.update_btn.setText("CHECKING...")

        worker = threading.Thread(target=self._check_for_updates_worker, args=(interactive,), daemon=True)
        worker.start()

    def _check_for_updates_worker(self, interactive: bool):
        try:
            info = self.updater.check_for_updates()
            QTimer.singleShot(0, lambda: self._on_update_manifest(interactive, info))
        except UpdateError as exc:
            QTimer.singleShot(0, lambda: self._on_update_check_error(interactive, str(exc)))

    def _on_update_check_error(self, interactive: bool, message: str):
        logging.warning(message)
        self.update_btn.setEnabled(True)
        self.update_btn.setText("⬇  UPDATE")
        if interactive:
            QMessageBox.warning(self, "Actualizacion", f"No se pudo comprobar actualizaciones.\n\n{message}")

    def _on_update_manifest(self, interactive: bool, info: dict):
        self.update_btn.setEnabled(True)
        self.update_btn.setText("⬇  UPDATE")

        if not info.get("update_available", False):
            if interactive:
                QMessageBox.information(self, "Actualizacion", f"Ya tienes la ultima version ({APP_VERSION}).")
            return

        latest_version = info.get("version", "?")
        release_notes = info.get("notes", "Sin notas de version.")
        force_update = bool(info.get("force", False))
        download_url = info.get("download_url", "")
        checksum = info.get("sha256")

        skipped_version = self.settings.value("skipped_update_version", "", type=str)
        if (not interactive) and (not force_update) and (skipped_version == str(latest_version)):
            logging.info(f"Actualizacion {latest_version} omitida previamente por el usuario")
            return

        if not download_url:
            logging.error("Manifest sin download_url")
            if interactive:
                QMessageBox.warning(self, "Actualizacion", "El servidor no devolvio una URL de descarga valida.")
            return

        msg = (
            f"Hay una nueva version disponible: {latest_version}\n"
            f"Tu version actual: {APP_VERSION}\n\n"
            f"Notas:\n{release_notes}\n\n"
            "Quieres descargar e instalar ahora?"
        )
        if force_update:
            msg = msg + "\n\nEsta actualizacion es obligatoria."

        buttons = QMessageBox.Yes | QMessageBox.No
        if force_update:
            buttons = QMessageBox.Yes

        decision = QMessageBox.question(self, "Actualizacion disponible", msg, buttons)
        if decision != QMessageBox.Yes:
            if not force_update:
                self.settings.setValue("skipped_update_version", str(latest_version))
            return

        # Clear skip if user accepts update
        self.settings.setValue("skipped_update_version", "")

        self._start_update_download(download_url, checksum, latest_version)

    def _start_update_download(self, download_url: str, checksum: str, latest_version: str):
        self.update_in_progress = True
        self.update_btn.setEnabled(False)
        self.update_btn.setText("DOWNLOADING...")

        worker = threading.Thread(
            target=self._download_update_worker,
            args=(download_url, checksum, latest_version),
            daemon=True,
        )
        worker.start()

    def _download_update_worker(self, download_url: str, checksum: str, latest_version: str):
        try:
            logging.info(f"Descargando actualizacion {latest_version} desde {download_url}")
            installer_path = self.updater.download_update(download_url=download_url, expected_sha256=checksum)
            QTimer.singleShot(0, lambda: self._on_update_downloaded(str(installer_path)))
        except UpdateError as exc:
            QTimer.singleShot(0, lambda: self._on_update_download_error(str(exc)))

    def _on_update_download_error(self, message: str):
        logging.error(message)
        self.update_in_progress = False
        self.update_btn.setEnabled(True)
        self.update_btn.setText("⬇  UPDATE")
        QMessageBox.warning(self, "Actualizacion", f"No se pudo completar la actualizacion.\n\n{message}")

    def _on_update_downloaded(self, installer_path: str):
        logging.info(f"Instalador descargado en {installer_path}")
        self.update_in_progress = False
        self.update_btn.setEnabled(True)
        self.update_btn.setText("⬇  UPDATE")

        QMessageBox.information(
            self,
            "Actualizacion descargada",
            "Se iniciara el instalador. La aplicacion se cerrara para completar la actualizacion.",
        )

        try:
            self.updater.launch_installer(Path(installer_path))
            QApplication.quit()
        except UpdateError as exc:
            QMessageBox.warning(self, "Actualizacion", f"No se pudo iniciar el instalador.\n\n{exc}")

    def poll_logs(self):
        val = log_stream.getvalue()
        if val:
            self.signals.log_update.emit(val)
            log_stream.truncate(0)
            log_stream.seek(0)

    def append_log(self, text):
        self.log_area.moveCursor(QTextCursor.End)
        self.log_area.insertPlainText(text)
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())

    def check_autostart(self):
        if sys.platform != 'win32':
            return False
        import winreg as reg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "MobilWheelServer"
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_READ)
            value, _ = reg.QueryValueEx(key, app_name)
            reg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            logging.error(f"Error checking autostart: {e}")
            return False

    def toggle_autostart(self, state):
        if sys.platform != 'win32':
            return
        import winreg as reg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "MobilWheelServer"
        
        if getattr(sys, 'frozen', False):
            command = f'"{sys.executable}"'
        else:
            command = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
            
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_ALL_ACCESS)
            if state == Qt.Checked:
                reg.SetValueEx(key, app_name, 0, reg.REG_SZ, command)
                logging.info("Added to Windows startup")
            else:
                try:
                    reg.DeleteValue(key, app_name)
                    logging.info("Removed from Windows startup")
                except FileNotFoundError:
                    pass
            reg.CloseKey(key)
        except Exception as e:
            logging.error(f"Failed to set autostart: {e}")

    def _set_status_pill(self, running: bool):
        if running:
            self.status_pill.setText("  ●  ONLINE  ")
            self.status_pill.setStyleSheet(
                "color: #FAFAFA;" # White
                "background-color: transparent;"
                "border: 1px solid #FAFAFA;"
                "border-radius: 6px;"
                "padding: 4px 14px;"
                "letter-spacing: 2px;"
                "font-weight: bold;"
                "font-size: 9px;"
            )
            self.status_pill.setGraphicsEffect(None)
        else:
            self.status_pill.setText("  ●  OFFLINE  ")
            self.status_pill.setStyleSheet(
                "color: #F97316;" # Orange
                "background-color: transparent;"
                "border: 1px solid #F97316;"
                "border-radius: 6px;"
                "padding: 4px 14px;"
                "letter-spacing: 2px;"
                "font-weight: bold;"
                "font-size: 9px;"
            )
            self.status_pill.setGraphicsEffect(None)

    def start_server(self):
        if not self.server_running.is_set():
            self.server_running.set()
            logging.info("Server is starting...")
            self.server_thread = threading.Thread(target=self.run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.restart_btn.setEnabled(True)
            self._set_status_pill(True)
            self.status_indicator.setToolTip("Server Running")

    def stop_server(self):
        if self.server_running.is_set():
            self.server_running.clear()
            logging.info("Server is stopping...")
            server_module.shutdown_event.set()
            self.server_thread.join()
            server_module.shutdown_event.clear()
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.restart_btn.setEnabled(False)
            self._set_status_pill(False)
            self.status_indicator.setToolTip("Server Stopped")

    def restart_server(self):
        if self.server_running.is_set():
            logging.info("Restarting server...")
            self.stop_server()
            # Wait a bit for the port to be freed
            QTimer.singleShot(1000, self.start_server)

    def run_server(self):
        try:
            logging.info("Starting server with UI callback")
            server_module.start_server(self.update_ui_callback)
        except Exception as e:
            logging.error(f"Server encountered an error: {e}")

    def update_ui_callback(self, command, value=None):
        if command in ['accelerate', 'brake', 'steering']:
            self.signals.update_axis.emit(command, value)
        elif command in ['left_top', 'right_top', 'left_bottom', 'right_bottom', 'volume_up', 'volume_down']:
            self.signals.toggle_button.emit(command)

    def update_progress_bars(self, command, value):
        if command == 'accelerate':
            self.accel_bar.setValue(value)
        elif command == 'brake':
            self.brake_bar.setValue(value)
        elif command == 'steering':
            self.steer_bar.setValue(value)

    def toggle_button_check(self, button_name):
        if button_name in self.buttons:
            logging.info(f"UI received button press for {button_name}.")
            cb = self.buttons[button_name]
            cb.setChecked(True)
            QTimer.singleShot(200, lambda: cb.setChecked(False))

    def closeEvent(self, event):
        if self.server_running.is_set():
            self.stop_server()
        self.telemetry_auto_detect_active = False
        if TELEMETRY_AVAILABLE and self.telemetry_connected:
            self.disconnect_telemetry()
        event.accept()

    # --- Game Telemetry Methods ---
    def start_telemetry_auto_detect(self):
        self.telemetry_auto_detect_active = True
        self.telemetry_status_lbl.setText("● Searching for game...")
        self.telemetry_status_lbl.setStyleSheet("color: #FFD60A; font-weight: bold;")
        self.try_telemetry_auto_connect()

    def try_telemetry_auto_connect(self):
        if not self.telemetry_auto_detect_active or self.telemetry_connected:
            return
        
        try:
            if not self.telemetry_reader:
                self.telemetry_reader = GameTelemetryReader()
            
            if self.telemetry_reader.connect():
                if self.telemetry_reader.start_polling(callback=self.on_telemetry_update, poll_rate=0.05):
                    self.telemetry_connected = True
                    self.telemetry_auto_detect_active = False
                    self.telemetry_disconnect_btn.setEnabled(True)
                    game_name = self.telemetry_reader.current_game or "Game"
                    self.telemetry_status_lbl.setText(f"● Connected ({game_name})")
                    self.telemetry_status_lbl.setStyleSheet("color: #00FF00; font-weight: bold;")
                    logging.info(f"Auto-connected to {game_name} telemetry")
                    return
                else:
                    self.telemetry_reader.disconnect()
        except Exception:
            pass
        
        if self.telemetry_auto_detect_active:
            QTimer.singleShot(2000, self.try_telemetry_auto_connect)

    def disconnect_telemetry(self):
        if self.telemetry_reader:
            self.telemetry_reader.stop_polling()
            self.telemetry_reader = None

        self.telemetry_connected = False
        self.telemetry_disconnect_btn.setEnabled(False)

        self.telemetry_speed_val.setText("---")
        self.telemetry_gear_val.setText("-")
        self.telemetry_rpm_bar.setValue(0)
        self.telemetry_rpm_val.setText("0")
        self.telemetry_gas_bar.setValue(0)
        self.telemetry_gas_lbl.setText("0%")
        self.telemetry_brake_bar.setValue(0)
        self.telemetry_brake_lbl.setText("0%")

        logging.info("Disconnected from game telemetry")
        self.start_telemetry_auto_detect()

    def on_telemetry_update(self, data: GamePhysics):
        self.signals.telemetry_update.emit(data)

    def update_telemetry_ui(self, data):
        try:
            self.telemetry_speed_val.setText(f"{data.speed_kmh:.0f}")

            if data.gear > 0:
                gear_text = str(data.gear)
            elif data.gear == 0:
                gear_text = "N"
            else:
                gear_text = "R"
            self.telemetry_gear_val.setText(gear_text)

            rpm = min(data.rpms, 8000)
            self.telemetry_rpm_bar.setValue(rpm)
            self.telemetry_rpm_val.setText(str(data.rpms))

            gas_pct = int(data.gas * 100)
            self.telemetry_gas_bar.setValue(gas_pct)
            self.telemetry_gas_lbl.setText(f"{gas_pct}%")

            brk_pct = int(data.brake * 100)
            self.telemetry_brake_bar.setValue(brk_pct)
            self.telemetry_brake_lbl.setText(f"{brk_pct}%")
        except Exception as e:
            logging.error(f"Error updating telemetry UI: {e}")

if __name__ == "__main__":
    # Enable crisp rendering on high-DPI displays
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Solid base to override with QSS
    window = ServerApp()
    window.show()
    sys.exit(app.exec_())
