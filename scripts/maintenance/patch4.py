import io

with io.open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

update_func = '''
    def on_language_changed(self, index):
        langs = ["en", "es", "ca"]
        set_language(langs[index])
        self.update_ui_strings()

    def update_ui_strings(self):
        self.lbl_lang.setText(tr("lang_label"))
        # self.status_pill is handled when status changes, but let's do a soft update
        if server_module.server_running.is_set():
            self.status_pill.setText(tr("pill_online"))
            self.status_label.setText(tr("status_run"))
            self.start_btn.setText(tr("btn_stop"))
        else:
            self.status_pill.setText(tr("pill_offline"))
            self.status_label.setText(tr("status_stop"))
            self.start_btn.setText(tr("btn_start"))
        
        self.vjoy_btn.setText(tr("btn_vjoy"))
        self.about_btn.setText(tr("btn_about"))
        
        # Sections
        if hasattr(self, 'lbl_sec_control'): self.lbl_sec_control.setText(tr("sec_control"))
        if hasattr(self, 'lbl_sec_logs'): self.lbl_sec_logs.setText(tr("sec_logs"))
        if hasattr(self, 'lbl_sec_misc'): self.lbl_sec_misc.setText(tr("sec_misc"))
        if hasattr(self, 'lbl_sec_tele'): self.lbl_sec_tele.setText(tr("sec_telemetry"))
        if hasattr(self, 'lbl_sec_axis'): self.lbl_sec_axis.setText(tr("sec_axis"))
        if hasattr(self, 'lbl_sec_btns'): self.lbl_sec_btns.setText(tr("sec_buttons"))
        
        # Checkboxes
        self.startup_cb.setText(tr("cb_startup"))
        self.autostart_server_cb.setText(tr("cb_autostart_srv"))
        self.autoupdate_cb.setText(tr("cb_autoupdate"))
        
        # Mini headers
        if hasattr(self, 'lbl_gas'): self.lbl_gas.setText(tr("gas"))
        if hasattr(self, 'lbl_brake'): self.lbl_brake.setText(tr("brake"))
        
        # Updates btn
        if hasattr(self, 'update_btn'): self.update_btn.setText(tr("upd_btn"))

'''

text = text.replace('def start_server(self):', update_func.strip() + '\\n\\n    def start_server(self):')

with io.open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Patch 4 applied")
