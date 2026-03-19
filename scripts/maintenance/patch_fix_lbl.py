import sys
with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix the incorrect replacements
text = text.replace('self.telemetry_self.lbl_gas', 'self.telemetry_gas_lbl')
text = text.replace('self.telemetry_self.lbl_brake', 'self.telemetry_brake_lbl')

with open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)

