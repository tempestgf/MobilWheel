import io

with io.open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

cb_patch = '''
        self.lang_cb = QComboBox()
        self.lang_cb.addItems(["English", "Español", "Català"])
        self.lang_cb.setCurrentIndex(1) # es is default for testing
        self.lang_cb.setStyleSheet("""
            QComboBox {
                border: 1px solid #3F3F46;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: #18181B;
                color: #FAFAFA;
                font-family: 'Segoe UI';
                font-size: 13px;
                min-width: 90px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #18181B;
                color: #FAFAFA;
                border: 1px solid #3F3F46;
                selection-background-color: #F97316;
            }
        """)
        self.lang_cb.currentIndexChanged.connect(self.on_language_changed)

        lang_layout = QHBoxLayout()
        self.lbl_lang = QLabel(tr("lang_label"))
        self.lbl_lang.setStyleSheet("color: #A1A1AA; font-size: 13px;")
        lang_layout.addWidget(self.lbl_lang)
        lang_layout.addWidget(self.lang_cb)
        
        right_col.addLayout(lang_layout)
        right_col.addWidget(self.status_pill, alignment=Qt.AlignRight)
'''

text = text.replace('right_col.addWidget(self.status_pill, alignment=Qt.AlignRight)', cb_patch)

# Add update_ui_strings and on_language_changed to ServerApp class
update_func = '''
    def on_language_changed(self, index):
        langs = ["en", "es", "ca"]
        set_language(langs[index])
        self.update_ui_strings()

    def update_ui_strings(self):
        self.lbl_lang.setText(tr("lang_label"))
        # self.status_pill is handled when status changes, but let's do a soft update
        if not server_running.is_set():
            self.status_pill.setText(tr("pill_offline"))
            self.status_label.setText(tr("status_stop"))
            self.start_btn.setText(tr("btn_start"))
        else:
            self.status_pill.setText(tr("pill_online"))
            self.status_label.setText(tr("status_run"))
            self.start_btn.setText(tr("btn_stop"))
        
        self.vjoy_btn.setText(tr("btn_vjoy"))
        self.about_btn.setText(tr("btn_about"))
        
        # Sections
        # We need to find the labels that are dynamically created if they are accessible
        # For statically created, we can just grab them if we mapped them
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

    # ... existing methods ...
'''

# Find a good place to put it: next to toggle_server
text = text.replace('def toggle_server(self):', update_func.strip() + '\\n\\n    def toggle_server(self):')

with io.open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Patch 3 applied")
