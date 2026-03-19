import sys
with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,', 'from PyQt5.QtWidgets import (QApplication, QListView, QMainWindow, QWidget, QVBoxLayout,')

with open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)
