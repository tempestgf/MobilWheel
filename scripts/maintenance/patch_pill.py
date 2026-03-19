import sys
with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('self.telemetry_status_lbl = QLabel("●  Searching for game...")', 'self.telemetry_status_lbl = QLabel(self.tr("pill_search"))')

text = text.replace('        if hasattr(self, \'lbl_axis_steer\'): self.lbl_axis_steer.setText(tr("steer"))', '        if hasattr(self, \'lbl_axis_steer\'): self.lbl_axis_steer.setText(tr("steer"))\n        if hasattr(self, \'telemetry_status_lbl\') and self.telemetry_status_lbl.text().startswith("●"): self.telemetry_status_lbl.setText(tr("pill_search"))')

with open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)
