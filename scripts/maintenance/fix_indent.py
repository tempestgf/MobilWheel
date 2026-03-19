import sys
import re

with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Make sure we only add it once!
text = re.sub(r'([ \t]+)tele_frame = QFrame\(\)', r'\1tele_frame = QFrame()\n\1tele_frame.setGraphicsEffect(self._make_shadow(25, QColor(0,0,0,120), (0,4)))', text)
text = re.sub(r'([ \t]+)axis_frame = QFrame\(\)', r'\1axis_frame = QFrame()\n\1axis_frame.setGraphicsEffect(self._make_shadow(25, QColor(0,0,0,120), (0,4)))', text)
text = re.sub(r'([ \t]+)btn_frame = QFrame\(\)', r'\1btn_frame = QFrame()\n\1btn_frame.setGraphicsEffect(self._make_shadow(25, QColor(0,0,0,120), (0,4)))', text)

with open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)
