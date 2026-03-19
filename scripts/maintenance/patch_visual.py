import sys
with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Enhance QSS
old_qss = '''        /* ── Scrollbars ──────────────────────────────────────────── */        
        QScrollBar:vertical {
            border: none;
            background: #0A0A0A;
            width: 8px;
            border-radius: 4px;
        }'''

new_qss = '''        /* ── ComboBox ────────────────────────────────────────────── */
        QComboBox {
            background-color: #171717;
            color: #FAFAFA;
            border: 1px solid #404040;
            border-radius: 4px;
            padding: 2px 8px;
            min-width: 75px;
        }
        QComboBox:hover {
            border: 1px solid #F97316;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 0px;
        }
        QComboBox QAbstractItemView {
            background-color: #171717;
            color: #FAFAFA;
            border: 1px solid #404040;
            selection-background-color: #F97316;
            selection-color: #0A0A0A;
            border-radius: 4px;
            outline: none;
        }
        /* ── Scrollbars ──────────────────────────────────────────── */        
        QScrollBar:vertical {
            border: none;
            background: #0A0A0A;
            width: 8px;
            border-radius: 4px;
        }'''
text = text.replace(old_qss, new_qss)

# Drop shadows for panels
old_shadow_1 = 'tele_frame = QFrame()'
new_shadow_1 = 'tele_frame = QFrame()\n        tele_frame.setGraphicsEffect(self._make_shadow(25, QColor(0,0,0,120), (0,4)))'
text = text.replace(old_shadow_1, new_shadow_1)

old_shadow_2 = 'axis_frame = QFrame()'
new_shadow_2 = 'axis_frame = QFrame()\n        axis_frame.setGraphicsEffect(self._make_shadow(25, QColor(0,0,0,120), (0,4)))'
text = text.replace(old_shadow_2, new_shadow_2)

old_shadow_3 = 'btn_frame = QFrame()'
new_shadow_3 = 'btn_frame = QFrame()\n        btn_frame.setGraphicsEffect(self._make_shadow(25, QColor(0,0,0,120), (0,4)))'
text = text.replace(old_shadow_3, new_shadow_3)

# Remove the inline QComboBox styling to let global QSS apply
text = text.replace('self.lang_cb.setStyleSheet("background-color: #2D2D2D; color: #FAFAFA; border: 1px solid #3D3D3D; border-radius: 4px; padding: 2px 5px;")', '')

with open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)
