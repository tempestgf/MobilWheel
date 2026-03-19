import sys
import re

with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

combo_qss = '''
        /* ── ComboBox ────────────────────────────────────────────── */
        QComboBox {
            background-color: #171717;
            color: #FAFAFA;
            border: 1px solid #404040;
            border-radius: 4px;
            padding: 4px 10px;
            min-height: 20px;
            font-weight: 500;
        }
        QComboBox:hover {
            border: 1px solid #F97316;
            background-color: #262626;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 24px;
            border-left: 1px solid #404040;
        }
        QComboBox::down-arrow {
            width: 10px;
            height: 10px;
            /* Simple CSS triangle approximation won't work easily here, so we just use border tricks if possible, 
               but PyQt standard arrows are fine if the background is defined. */
        }
        QComboBox QAbstractItemView {
            background-color: #1A1A1A;
            color: #FAFAFA;
            border: 1px solid #F97316;
            selection-background-color: #F97316;
            selection-color: #0A0A0A;
            outline: none;
            padding: 4px;
        }
        QComboBox QAbstractItemView::item {
            min-height: 28px;
            padding-left: 5px;
            border-radius: 4px;
        }
        QComboBox QAbstractItemView::item:hover {
            background-color: #333333;
        }
'''

# Insert the combo qss right before /* ── Scrollbars
text = text.replace('        /* ── Scrollbars ', combo_qss + '\n        /* ── Scrollbars ')

# Add QLineEdit styling as well just in case
lineedit_qss = '''
        /* ── LineEdit / Generic inputs ────────────────────────────── */
        QLineEdit {
            background-color: #171717;
            color: #FAFAFA;
            border: 1px solid #404040;
            border-radius: 4px;
            padding: 4px 8px;
        }
        QLineEdit:focus {
            border: 1px solid #F97316;
        }
'''
text = text.replace('        /* ── Scrollbars ', lineedit_qss + '\n        /* ── Scrollbars ')

# Improve the check boxes a bit more
text = text.replace('QCheckBox::indicator:hover  { border: 1px solid #F97316; }', 'QCheckBox::indicator:hover  { border: 1px solid #F97316; background-color: #262626; }')


with open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)
