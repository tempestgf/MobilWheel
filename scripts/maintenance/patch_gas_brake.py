import sys
with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix GAS label layout and translation reference
text = text.replace('gas_lbl = QLabel("GAS")', 'self.lbl_gas = QLabel("GAS")')
text = text.replace('gas_lbl.setFont', 'self.lbl_gas.setFont')
text = text.replace('gas_lbl.setStyleSheet', 'self.lbl_gas.setStyleSheet')
text = text.replace('gas_lbl.setFixedWidth(40)', 'self.lbl_gas.setMinimumWidth(80)')
text = text.replace('tele_grid.addWidget(gas_lbl,                  3, 0)', 'tele_grid.addWidget(self.lbl_gas,                  3, 0)')

# Fix BRAKE label layout and translation reference
text = text.replace('brk_lbl = QLabel("BRAKE")', 'self.lbl_brake = QLabel("BRAKE")')
text = text.replace('brk_lbl.setFont', 'self.lbl_brake.setFont')
text = text.replace('brk_lbl.setStyleSheet', 'self.lbl_brake.setStyleSheet')
text = text.replace('brk_lbl.setFixedWidth(40)', 'self.lbl_brake.setMinimumWidth(80)')
text = text.replace('tele_grid.addWidget(brk_lbl,                  4, 0)', 'tele_grid.addWidget(self.lbl_brake,                  4, 0)')

with open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)

