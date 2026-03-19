import sys
with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('from PyQt5.QtWidgets import QMainWindow,', 'from PyQt5.QtWidgets import QMainWindow, QListView,')

with open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)
