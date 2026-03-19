import sys
with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Make the cards and stats labels instance attributes so they can update
text = text.replace('def _make_stat_card(self, title, value_widget):', 'def _make_stat_card(self, title, value_widget):\n        return self._make_stat_card_dyn(title, value_widget)[0]')

new_func = """
    def _make_stat_card_dyn(self, title, value_widget):
        card = QFrame()
        card.setObjectName("StatCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)
        t = QLabel(title)
        t.setFont(QFont("Segoe UI", 7, QFont.DemiBold))
        t.setAlignment(Qt.AlignCenter)
        t.setStyleSheet("color: #8E8E8E; letter-spacing: 1px;")
        layout.addWidget(t)
        layout.addWidget(value_widget)
        return card, t

    def axis_row_dyn(self, label_text, bar_widget, accent_color):
        row = QHBoxLayout()
        row.setSpacing(12)
        lbl = QLabel(label_text)
        lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
        lbl.setStyleSheet(f"color: {accent_color}; min-width: 82px; letter-spacing: 1px;") # Fixed min-width for responsive languages
        row.addWidget(lbl)
        row.addWidget(bar_widget, 1)
        return row, lbl
"""

# Append new_func to ServerApp class
text = text.replace("def _make_stat_card(self, title, value_widget):", new_func + "\n    def _make_stat_card(self, title, value_widget):")

# Update usages inside init_ui for telemetry stats
text = text.replace('speed_card = self._make_stat_card("SPEED  km/h", self.telemetry_speed_val)', 'speed_card, self.lbl_speed_title = self._make_stat_card_dyn("SPEED km/h", self.telemetry_speed_val)')
text = text.replace('gear_card  = self._make_stat_card("GEAR",        self.telemetry_gear_val)', 'gear_card, self.lbl_gear_title = self._make_stat_card_dyn("GEAR", self.telemetry_gear_val)')
text = text.replace('rpm_card   = self._make_stat_card("RPM",         self.telemetry_rpm_val)', 'rpm_card, self.lbl_rpm_title = self._make_stat_card_dyn("RPM", self.telemetry_rpm_val)')

text = text.replace('        def axis_row(label_text, bar_widget, accent_color):', '# Removing axis_row')
text = text.replace('            row = QHBoxLayout()', '')
text = text.replace('            row.setSpacing(12)', '')
text = text.replace('            lbl = QLabel(label_text)', '')
text = text.replace('            lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))', '')
text = text.replace('            lbl.setStyleSheet(f"color: {accent_color}; min-width: 82px; letter-spacing: 1px;")', '')
text = text.replace('            row.addWidget(lbl)', '')
text = text.replace('            row.addWidget(bar_widget, 1)', '')
text = text.replace('            return row', '')

# Replace callers
text = text.replace('axis_outer.addLayout(axis_row("ACCELERATE", self.accel_bar, "#FAFAFA"))', 'row_a, self.lbl_axis_accel = self.axis_row_dyn("ACCELERATE", self.accel_bar, "#FAFAFA")\n        axis_outer.addLayout(row_a)')
text = text.replace('axis_outer.addLayout(axis_row("BRAKE",      self.brake_bar, "#F97316"))', 'row_b, self.lbl_axis_brake = self.axis_row_dyn("BRAKE", self.brake_bar, "#F97316")\n        axis_outer.addLayout(row_b)')
text = text.replace('axis_outer.addLayout(axis_row("STEERING",   self.steer_bar, "#FB923C"))', 'row_s, self.lbl_axis_steer = self.axis_row_dyn("STEERING", self.steer_bar, "#FB923C")\n        axis_outer.addLayout(row_s)')

# Add translated strings mapping to update_ui_strings
update_strings_additions = '''
        if hasattr(self, 'lbl_speed_title'): self.lbl_speed_title.setText(tr("speed"))
        if hasattr(self, 'lbl_gear_title'): self.lbl_gear_title.setText(tr("gear"))
        if hasattr(self, 'lbl_rpm_title'): self.lbl_rpm_title.setText(tr("rpm"))
        if hasattr(self, 'lbl_axis_accel'): self.lbl_axis_accel.setText(tr("accel"))
        if hasattr(self, 'lbl_axis_brake'): self.lbl_axis_brake.setText(tr("brake"))
        if hasattr(self, 'lbl_axis_steer'): self.lbl_axis_steer.setText(tr("steer"))
        if hasattr(self, 'lbl_gas'): self.lbl_gas.setText(tr("gas"))
        if hasattr(self, 'lbl_brake'): self.lbl_brake.setText(tr("brake"))
'''
text = text.replace('        if hasattr(self, \'lbl_gas\'): self.lbl_gas.setText(tr("gas"))', update_strings_additions)
text = text.replace('        if hasattr(self, \'lbl_brake\'): self.lbl_brake.setText(tr("brake"))\n', '')

# Make the window title also updated
text = text.replace('        self.lbl_lang.setText(tr("lang_label"))', '        self.setWindowTitle(tr("msg_about_title"))\n        self.lbl_lang.setText(tr("lang_label"))')

with open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)
