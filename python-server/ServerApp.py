import os
import sys
import threading
import logging
from io import StringIO

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel,
                             QProgressBar, QTextEdit, QGridLayout, QCheckBox,
                             QGraphicsDropShadowEffect, QFrame, QSizePolicy)
from PyQt5.QtCore import pyqtSignal, QObject, QTimer, Qt, QSettings
from PyQt5.QtGui import QIcon, QFont, QColor, QTextCursor, QPixmap, QPainter, QPainterPath, QFontDatabase, QLinearGradient, QPen, QBrush

# Configurar logging
log_stream = StringIO()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', stream=log_stream)

import xbox as server_module

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
class RacingStripe(QWidget):
    """Decorative horizontal accent stripe with a gradient."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(4)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0.0,  QColor(0,   0,   0,   0))
        grad.setColorAt(0.2,  QColor(255, 109,  0, 220))
        grad.setColorAt(0.6,  QColor(255, 214,  10, 255))
        grad.setColorAt(1.0,  QColor(255, 109,  0,  80))
        painter.fillRect(self.rect(), QBrush(grad))


class RacingGaugeBar(QProgressBar):
    """Custom progress bar that draws a gradient fill with a glowing edge."""
    def __init__(self, max_val=100, accent="#FF6D00", parent=None):
        super().__init__(parent)
        self.setMaximum(max_val)
        self.setTextVisible(False)
        self._accent = QColor(accent)
        self.setFixedHeight(16)
        # We fully paint our own background — skip Qt's redundant fill
        self.setAttribute(Qt.WA_OpaquePaintEvent)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        radius = 6

        # Track
        path_bg = QPainterPath()
        path_bg.addRoundedRect(r.x(), r.y(), r.width(), r.height(), radius, radius)
        painter.fillPath(path_bg, QColor("#0A0A0A"))
        painter.setPen(QPen(QColor("#1F1F1F"), 1))
        painter.drawPath(path_bg)

        # Fill
        ratio = self.value() / max(self.maximum(), 1)
        fill_w = int(r.width() * ratio)
        if fill_w > 2:
            grad = QLinearGradient(0, 0, fill_w, 0)
            grad.setColorAt(0.0, self._accent.darker(140))
            grad.setColorAt(0.6, self._accent)
            grad.setColorAt(1.0, QColor("#FFD60A"))
            fill_path = QPainterPath()
            fill_path.addRoundedRect(r.x(), r.y(), fill_w, r.height(), radius, radius)
            painter.fillPath(fill_path, QBrush(grad))

            # Glow edge
            glow_pen = QPen(QColor(255, 214, 10, 80), 3)
            painter.setPen(glow_pen)
            painter.drawLine(fill_w, r.y() + 2, fill_w, r.bottom() - 2)


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

        # Auto-start server if setting is enabled
        if self.settings.value("auto_start_server", False, type=bool):
            QTimer.singleShot(500, self.start_server)

    def _make_shadow(self, blur=20, color=QColor(255, 109, 0, 80), offset=(0, 5)):
        s = QGraphicsDropShadowEffect()
        s.setBlurRadius(blur)
        s.setColor(color)
        s.setOffset(*offset)
        return s

    def _section_label(self, text):
        """Small orange uppercase section divider label."""
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
        lbl.setStyleSheet(
            "color: #FF6D00;"
            "letter-spacing: 4px;"
            "margin-top: 6px;"
            "margin-bottom: 2px;"
        )
        return lbl

    def _value_label(self, text, size=22):
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
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        t = QLabel(title)
        t.setFont(QFont("Segoe UI", 7, QFont.Bold))
        t.setAlignment(Qt.AlignCenter)
        t.setStyleSheet("color: #555555; letter-spacing: 2px;")
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
        main_layout.addWidget(RacingStripe())

        # ── Inner content (NO scroll — responsive direct layout) ──────────
        inner = QVBoxLayout()
        inner.setSpacing(8)
        inner.setContentsMargins(28, 12, 28, 12)
        main_layout.addLayout(inner, stretch=1)

        # ── HEADER ───────────────────────────────────────────────────────
        header_layout = QHBoxLayout()
        header_layout.setSpacing(0)

        logo_label = QLabel()
        logo_path = os.path.join(self.base_path, "app_logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setGraphicsEffect(self._make_shadow(24, QColor(255, 109, 0, 90), (0, 0)))

        title_layout = QVBoxLayout()
        title_layout.setSpacing(1)
        title_layout.setContentsMargins(12, 0, 0, 0)
        title_label = QLabel("GENEON")
        title_label.setFont(QFont(self.museo_font_family, 30, QFont.Bold))
        title_label.setStyleSheet("color: #FFFFFF; letter-spacing: 3px;")
        subtitle_label = QLabel("MOBILE WHEEL SERVER")
        subtitle_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        subtitle_label.setStyleSheet("color: #FF6D00; letter-spacing: 7px;")
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
            "color: #FF3B30; background-color: #1A0000;"
            "border: 1px solid #FF3B30; border-radius: 10px;"
            "padding: 3px 12px; letter-spacing: 2px;"
        )
        self.status_pill.setGraphicsEffect(self._make_shadow(10, QColor(255, 59, 48, 80), (0, 0)))
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
        cb_row.addWidget(self.autostart_app_cb)
        cb_row.addWidget(self.autostart_server_cb)

        right_col.addWidget(self.status_pill, alignment=Qt.AlignRight)
        right_col.addLayout(cb_row)
        header_layout.addLayout(right_col)
        inner.addLayout(header_layout)

        # ── Racing stripe divider ─────────────────────────────────────────
        inner.addWidget(RacingStripe())

        # ── CONTROL BUTTONS ───────────────────────────────────────────────
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)

        self.start_btn = QPushButton("▶  START")
        self.start_btn.setObjectName("StartBtn")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setMinimumHeight(44)
        self.start_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.start_btn.clicked.connect(self.start_server)

        self.stop_btn = QPushButton("■  STOP")
        self.stop_btn.setObjectName("StopBtn")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setMinimumHeight(44)
        self.stop_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.stop_btn.clicked.connect(self.stop_server)
        self.stop_btn.setEnabled(False)

        self.restart_btn = QPushButton("↺  RESTART")
        self.restart_btn.setObjectName("RestartBtn")
        self.restart_btn.setCursor(Qt.PointingHandCursor)
        self.restart_btn.setMinimumHeight(44)
        self.restart_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.restart_btn.clicked.connect(self.restart_server)
        self.restart_btn.setEnabled(False)

        self.start_btn.setGraphicsEffect(self._make_shadow(20, QColor(255, 109, 0, 90), (0, 4)))
        control_layout.addWidget(self.start_btn, 2)
        control_layout.addWidget(self.stop_btn, 1)
        control_layout.addWidget(self.restart_btn, 1)
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
            self.telemetry_status_lbl.setStyleSheet("color: #FFD60A;")
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
            self.telemetry_rpm_bar = RacingGaugeBar(8000, "#FF3B30")
            tele_grid.addWidget(self.telemetry_rpm_bar, 2, 0, 1, 4)

            # Row 3 — Gas bar
            gas_lbl = QLabel("GAS")
            gas_lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
            gas_lbl.setStyleSheet("color: #34C759; letter-spacing: 2px;")
            gas_lbl.setFixedWidth(40)
            self.telemetry_gas_bar = RacingGaugeBar(100, "#34C759")
            self.telemetry_gas_lbl = QLabel("0%")
            self.telemetry_gas_lbl.setFont(QFont("Consolas", 10, QFont.Bold))
            self.telemetry_gas_lbl.setStyleSheet("color: #34C759;")
            self.telemetry_gas_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.telemetry_gas_lbl.setFixedWidth(38)
            tele_grid.addWidget(gas_lbl,                  3, 0)
            tele_grid.addWidget(self.telemetry_gas_bar,   3, 1, 1, 2)
            tele_grid.addWidget(self.telemetry_gas_lbl,   3, 3)

            # Row 4 — Brake bar
            brk_lbl = QLabel("BRAKE")
            brk_lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
            brk_lbl.setStyleSheet("color: #FF3B30; letter-spacing: 2px;")
            brk_lbl.setFixedWidth(40)
            self.telemetry_brake_bar = RacingGaugeBar(100, "#FF3B30")
            self.telemetry_brake_lbl = QLabel("0%")
            self.telemetry_brake_lbl.setFont(QFont("Consolas", 10, QFont.Bold))
            self.telemetry_brake_lbl.setStyleSheet("color: #FF3B30;")
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
            lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
            lbl.setStyleSheet(f"color: {accent_color}; min-width: 82px; letter-spacing: 1px;")
            row.addWidget(lbl)
            row.addWidget(bar_widget, 1)
            return row

        self.accel_bar = RacingGaugeBar(100,   "#34C759")
        self.brake_bar = RacingGaugeBar(100,   "#FF3B30")
        self.steer_bar = RacingGaugeBar(32767, "#FF6D00")
        axis_outer.addLayout(axis_row("ACCELERATE", self.accel_bar, "#34C759"))
        axis_outer.addLayout(axis_row("BRAKE",      self.brake_bar, "#FF3B30"))
        axis_outer.addLayout(axis_row("STEERING",   self.steer_bar, "#FF6D00"))
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
            background-color: #070707;
        }
        QWidget {
            color: #DCDCDC;
            font-family: 'Segoe UI', sans-serif;
            background-color: transparent;
        }
        #ContentWidget {
            background-color: #070707;
        }

        /* ── Section frames (Telemetry / Axis / Buttons) ─────────── */
        #TelemetryFrame, #AxisFrame, #BtnFrame {
            background-color: #0D0D0D;
            border: 1px solid #1E1E1E;
            border-radius: 12px;
        }
        /* Left accent bar on each section frame */
        #TelemetryFrame {
            border-left: 3px solid #FF3B30;
        }
        #AxisFrame {
            border-left: 3px solid #FF6D00;
        }
        #BtnFrame {
            border-left: 3px solid #FFD60A;
        }

        /* ── Stat cards ──────────────────────────────────────────── */
        #StatCard {
            background-color: #111111;
            border: 1px solid #242424;
            border-radius: 10px;
        }

        /* ── Buttons ─────────────────────────────────────────────── */
        QPushButton {
            background-color: #111111;
            border: 1px solid #2A2A2A;
            color: #888888;
            padding: 10px 18px;
            border-radius: 10px;
            font-weight: 800;
            font-size: 13px;
            letter-spacing: 3px;
        }
        QPushButton:hover {
            background-color: #181818;
            border: 1px solid #FF6D00;
            color: #FF6D00;
        }
        QPushButton:pressed {
            background-color: #FF6D00;
            color: #000000;
            border: 1px solid #FF6D00;
        }
        QPushButton:disabled {
            border: 1px solid #1A1A1A;
            color: #2E2E2E;
            background-color: #0A0A0A;
        }
        /* START button — highlighted */
        #StartBtn {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1A0900, stop:1 #1F1000);
            border: 1px solid #FF6D00;
            color: #FF6D00;
        }
        #StartBtn:hover {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #FF6D00, stop:1 #FFD60A);
            color: #000000;
            border: 1px solid #FFD60A;
        }
        #StartBtn:disabled {
            background-color: #0A0A0A;
            border: 1px solid #1A1A1A;
            color: #2E2E2E;
        }
        /* Disconnect button */
        #DisconnectBtn {
            border: 1px solid #FF3B30;
            color: #FF3B30;
            background-color: #150000;
            font-size: 10px;
            letter-spacing: 2px;
        }
        #DisconnectBtn:hover {
            background-color: #FF3B30;
            color: #000000;
        }
        #DisconnectBtn:disabled {
            border: 1px solid #1A1A1A;
            color: #2E2E2E;
            background-color: #0A0A0A;
        }

        /* ── Checkboxes ──────────────────────────────────────────── */
        QCheckBox {
            spacing: 14px;
            color: #888888;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 1px;
        }
        QCheckBox:hover { color: #CCCCCC; }
        QCheckBox::indicator {
            width: 20px;
            height: 20px;
            border-radius: 5px;
            border: 2px solid #2A2A2A;
            background-color: #0D0D0D;
        }
        QCheckBox::indicator:hover  { border: 2px solid #FF6D00; }
        QCheckBox::indicator:checked {
            background-color: #FF6D00;
            border: 2px solid #FF6D00;
            image: none;
        }

        /* ── Log area ────────────────────────────────────────────── */
        QTextEdit {
            background-color: #080808;
            border: 1px solid #1A1A1A;
            border-radius: 10px;
            padding: 14px;
            color: #606060;
            font-size: 11px;
            selection-background-color: #FF6D00;
            selection-color: #000000;
        }

        /* ── Scrollbars ──────────────────────────────────────────── */
        QScrollBar:vertical {
            border: none;
            background: #080808;
            width: 6px;
            border-radius: 3px;
        }
        QScrollBar::handle:vertical {
            background: #252525;
            min-height: 30px;
            border-radius: 3px;
        }
        QScrollBar::handle:vertical:hover { background: #FF6D00; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none; background: none;
        }
        /* hide scroll on log area - only the log itself scrolls internally */
        QScrollBar:horizontal { height: 0px; }
        """
        self.setStyleSheet(qss)

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
                "color: #00FF80;"
                "background-color: #001A0D;"
                "border: 1px solid #00FF80;"
                "border-radius: 12px;"
                "padding: 4px 14px;"
                "letter-spacing: 2px;"
                "font-weight: bold;"
                "font-size: 9px;"
            )
            eff = self._make_shadow(16, QColor(0, 255, 100, 100), (0, 0))
            self.status_pill.setGraphicsEffect(eff)
        else:
            self.status_pill.setText("  ●  OFFLINE  ")
            self.status_pill.setStyleSheet(
                "color: #FF3B30;"
                "background-color: #1A0000;"
                "border: 1px solid #FF3B30;"
                "border-radius: 12px;"
                "padding: 4px 14px;"
                "letter-spacing: 2px;"
                "font-weight: bold;"
                "font-size: 9px;"
            )
            eff = self._make_shadow(12, QColor(255, 59, 48, 80), (0, 0))
            self.status_pill.setGraphicsEffect(eff)

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
