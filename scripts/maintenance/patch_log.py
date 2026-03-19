import sys
with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('background-color: #171717;\n            border: 1px solid #262626;\n            border-radius: 6px;\n            padding: 10px;\n            color: #D4D4D4;\n            font-size: 11px;\n            selection-background-color: #F97316;', 'background-color: #0F0F0F;\n            border: 1px solid #1E1E1E;\n            border-radius: 6px;\n            padding: 12px;\n            color: #D4D4D4;\n            font-size: 11px;\n            selection-background-color: #F97316;')

with open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)
