import re
with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = \"\"\"        cb_row = QHBoxLayout()
        cb_row.setSpacing(18)
        self.autostart_app_cb = QCheckBox("Startup")
        self.autostart_app_cb.setChecked(self.check_autostart())
        self.autostart_app_cb.stateChanged.connect(self.toggle_autostart)
        cb_row.addWidget(self.autostart_app_cb)
        
        # Added auto_update_cb if exists in previous code, let's just make it safe
        if hasattr(self, 'auto_update_cb'):
            cb_row.addWidget(self.auto_update_cb)

        # Language Selector
        lang_layout = QHBoxLayout()
        self.lbl_lang = QLabel(tr("lang_label"))
        self.lang_cb = QComboBox()
        self.lang_cb.addItems(["English", "Español", "Català"])
        curr_lang = config.get("language", "en")
        if curr_lang == "es": self.lang_cb.setCurrentIndex(1)
        elif curr_lang == "ca": self.lang_cb.setCurrentIndex(2)
        else: self.lang_cb.setCurrentIndex(0)
        self.lang_cb.currentIndexChanged.connect(self.on_language_changed)
        lang_layout.addWidget(self.lbl_lang)
        lang_layout.addWidget(self.lang_cb)
        
        right_col.addWidget(self.status_pill, alignment=Qt.AlignRight)
        right_col.addLayout(lang_layout)
        right_col.addLayout(cb_row)
        header_layout.addLayout(right_col)\"\"\"

text = re.sub(
    r"        cb_row = QHBoxLayout\(\)*?.*?header_layout\.addLayout\(right_col\)",
    replacement,
    text,
    flags=re.DOTALL
)

def fix_labels(t):
    rep = \"\"\"        if hasattr(self, 'lbl_lang'):
            self.lbl_lang.setText(tr("lang_label"))\"\"\"
    return re.sub(r'        self\.lbl_lang\.setText\(tr\("lang_label"\)\)', rep, t)

text = fix_labels(text)

with open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Done")
