import io

with io.open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('inner.addWidget(self._section_label(tr("sec_telemetry")))', '''self.lbl_sec_tele = self._section_label(tr("sec_telemetry"))\n        inner.addWidget(self.lbl_sec_tele)''')
text = text.replace('inner.addWidget(self._section_label(tr("sec_axis")))', '''self.lbl_sec_axis = self._section_label(tr("sec_axis"))\n        inner.addWidget(self.lbl_sec_axis)''')
text = text.replace('inner.addWidget(self._section_label(tr("sec_buttons")))', '''self.lbl_sec_btns = self._section_label(tr("sec_buttons"))\n        inner.addWidget(self.lbl_sec_btns)''')
text = text.replace('inner.addWidget(self._section_label(tr("sec_logs")))', '''self.lbl_sec_logs = self._section_label(tr("sec_logs"))\n        inner.addWidget(self.lbl_sec_logs)''')
text = text.replace('inner.addWidget(self._section_label("SERVER LOGS"))', '''self.lbl_sec_logs = self._section_label(tr("sec_logs"))\n        inner.addWidget(self.lbl_sec_logs)''')

with io.open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Patch 5 done")
