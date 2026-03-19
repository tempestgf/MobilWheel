import sys
with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('self.apply_stylesheet()', 'self.apply_stylesheet()\n        self.update_ui_strings()')

with open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)
