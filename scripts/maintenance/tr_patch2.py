import sys
with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('self.telemetry_status_lbl.setText("● Searching for game...")', 'self.telemetry_status_lbl.setText(tr("pill_search"))')
text = text.replace('self.telemetry_status_lbl.setText(f"● Connected ({game_name})")', 'self.telemetry_status_lbl.setText(tr("pill_conn").format(game_name))')
text = text.replace('self.telemetry_status_lbl.setText("●  Searching for game...")', 'self.telemetry_status_lbl.setText(tr("pill_search"))')

text = text.replace('msg.setWindowTitle("About Mobile Wheel Server")', 'msg.setWindowTitle(tr("msg_about_title"))')

with open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)
