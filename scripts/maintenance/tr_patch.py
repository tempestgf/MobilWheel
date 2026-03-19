import sys
with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re

new_code = '''        if hasattr(self, 'stop_btn'): self.stop_btn.setText(tr("btn_stop_short"))
        if hasattr(self, 'restart_btn'): self.restart_btn.setText(tr("btn_restart_short"))
        if hasattr(self, 'update_btn'): self.update_btn.setText(tr("btn_update_short"))
        if hasattr(self, 'telemetry_disconnect_btn'): self.telemetry_disconnect_btn.setText(tr("btn_disconnect"))'''

text = text.replace('        if hasattr(self, \'update_btn\'): self.update_btn.setText(tr("upd_btn"))', new_code)
text = text.replace('self.start_btn.setText(tr("btn_start"))', 'self.start_btn.setText(tr("btn_start_short"))')
text = text.replace('self.start_btn.setText(tr("btn_stop"))', 'self.start_btn.setText(tr("btn_stop_short"))')

# Replace tooltips
text = text.replace('self.status_indicator.setToolTip("Server Running")', 'self.status_indicator.setToolTip(tr("status_run"))')
text = text.replace('self.status_indicator.setToolTip("Server Stopped")', 'self.status_indicator.setToolTip(tr("status_stop"))')

with open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)
