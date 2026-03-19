import sys
with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Make sure we use QListView for the combo box drop down
text = text.replace('from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout,', 'from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QListView,')

old_cb = 'self.lang_cb.addItems(["English", "Español", "Català"])'
new_cb = '''self.lang_cb.addItems(["English", "Español", "Català"])
        self.lang_list_view = QListView()
        self.lang_cb.setView(self.lang_list_view)'''
text = text.replace(old_cb, new_cb)

with open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)
