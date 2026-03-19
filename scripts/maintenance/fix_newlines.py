import io

with io.open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\\n\\n    def start_server(self):', '\n\n    def start_server(self):')
text = text.replace('setText(tr("upd_btn"))\n\\\n\\n    def', 'setText(tr("upd_btn"))\n\n    def')
text = text.replace('setText(tr("upd_btn"))\\n\\n    def', 'setText(tr("upd_btn"))\n\n    def')

with io.open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)
