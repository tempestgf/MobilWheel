import sys
with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Make the title of stat cards dynamically change 
text = text.replace('self.lbl_speed_title.setText(tr("speed"))', 'self.lbl_speed_title.setText(tr("speed") + " km/h" if "km/h" not in tr("speed") else tr("speed"))')

# Expand text length for specific elements in responsive UI
text = text.replace('def axis_row_dyn(self, label_text, bar_widget, accent_color):', '''def axis_row_dyn(self, label_text, bar_widget, accent_color):''')
text = text.replace('lbl.setStyleSheet(f"color: {accent_color}; min-width: 82px; letter-spacing: 1px;")', 'lbl.setStyleSheet(f"color: {accent_color}; min-width: 105px; max-width: 130px; letter-spacing: 1px;")\n        lbl.setWordWrap(True)')

# Fix searching for game string
text = text.replace('self.telemetry_game_val.setText("Searching for game...")', 'self.telemetry_game_val.setText(self.tr("searching"))')
text = text.replace('self.telemetry_game_val.setText("Buscando juego...")', 'self.telemetry_game_val.setText(self.tr("searching"))')

with open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)
