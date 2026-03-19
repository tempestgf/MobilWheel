import sys
with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

msgbox_qss = '''
        /* ── MessageBox ──────────────────────────────────────────── */
        QMessageBox {
            background-color: #0A0A0A;
        }
        QMessageBox QLabel {
            color: #FAFAFA;
            font-size: 14px;
        }
        QMessageBox QPushButton {
            min-width: 60px;
        }
'''

text = text.replace('        /* ── Scrollbars ', msgbox_qss + '\n        /* ── Scrollbars ')

with open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)

