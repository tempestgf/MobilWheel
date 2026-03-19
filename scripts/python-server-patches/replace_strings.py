# -*- coding: utf-8 -*-
with open('ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

reps = {
    'QPushButton("▶  START")': 'QPushButton(tr(\'btn_start_short\'))',
    'QPushButton("■  STOP")': 'QPushButton(tr(\'btn_stop_short\'))',
    'QPushButton("↻  RESTART")': 'QPushButton(tr(\'btn_restart_short\'))',
    'QPushButton("⬇  UPDATE")': 'QPushButton(tr(\'btn_update_short\'))',
    'QPushButton("DISCONNECT")': 'QPushButton(tr(\'btn_disconnect\'))',
    'self.update_btn.setText("CHECKING...")': 'self.update_btn.setText(tr(\'btn_checking\'))',
    'self.update_btn.setText("DOWNLOADING...")': 'self.update_btn.setText(tr(\'btn_downloading\'))',
    'self.update_btn.setText("⬇  UPDATE")': 'self.update_btn.setText(tr(\'btn_update_short\'))',
    'gas_lbl = QLabel("GAS")': 'self.gas_lbl = QLabel(tr(\'gas\'))',
    'brk_lbl = QLabel("BRAKE")': 'self.brk_lbl = QLabel(tr(\'brake\'))',
    'QLabel("  ●  OFFLINE  ")': 'QLabel(tr(\'pill_offline\'))',
    'self.status_pill.setText("  ●  ONLINE  ")': 'self.status_pill.setText(tr(\'pill_online\'))',
    'self.status_pill.setText("  ●  OFFLINE  ")': 'self.status_pill.setText(tr(\'pill_offline\'))',
    'QLabel("●  Searching for game...")': 'QLabel(tr(\'pill_search\'))',
    'self.telemetry_status_lbl.setText("● Searching for game...")': 'self.telemetry_status_lbl.setText(tr(\'pill_search\'))',
    'self.telemetry_status_lbl.setText(f"● Connected ({game_name})")': 'self.telemetry_status_lbl.setText(tr(\'pill_conn\').format(game_name))',
}

for k,v in reps.items():
    text = text.replace(k, v)

with open('ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Replaced successfully")
