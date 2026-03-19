with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'QMessageBox' in line and '("' in line:
        print(f'{i}: {line.strip()}')
    elif 'setToolTip' in line and '("' in line:
        print(f'{i}: {line.strip()}')
    elif 'setWindowTitle' in line and '("' in line:
        print(f'{i}: {line.strip()}')
    elif 'QLabel("' in line or 'QPushButton("' in line or 'QCheckBox("' in line:
        print(f'{i}: {line.strip()}')
