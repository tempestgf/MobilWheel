import sys
import re
with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Enhance Status Pill to be actually round
text = re.sub(r'border-radius: 6px;(\"?\s*\"padding: \d+px)', r'border-radius: 12px;\1', text)
text = text.replace('"border: 1px solid #F97316; border-radius: 6px;"', '"border: 1px solid #F97316; border-radius: 12px;"')
text = text.replace('"border: 1px solid #FAFAFA;"\n                "border-radius: 6px;"', '"border: 1px solid #FAFAFA;"\n                "border-radius: 12px;"')
text = text.replace('"border: 1px solid #F97316;"\n                "border-radius: 6px;"', '"border: 1px solid #F97316;"\n                "border-radius: 12px;"')

# 2. Make Dashboard numbers bigger and pop more
text = text.replace('self.telemetry_speed_val = self._value_label("---", 18)', 'self.telemetry_speed_val = self._value_label("---", 24)')
text = text.replace('self.telemetry_gear_val  = self._value_label("-",   18)', 'self.telemetry_gear_val  = self._value_label("-",   24)')
text = text.replace('self.telemetry_rpm_val   = self._value_label("0",   16)', 'self.telemetry_rpm_val   = self._value_label("0",   20)')

# 3. Enhance Button Styles in QSS
old_btn_qss = '''        QPushButton {
            background-color: #171717;
            border: 1px solid #404040;
            color: #A3A3A3;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 12px;
            letter-spacing: 2px;
        }
        QPushButton:hover {
            background-color: #262626;
            border: 1px solid #F97316;
            color: #FAFAFA;
        }
        QPushButton:pressed {
            background-color: #F97316;
            color: #0A0A0A;
            border: 1px solid #F97316;
        }'''

new_btn_qss = '''        QPushButton {
            background-color: #1A1A1A;
            border: 1px solid #333333;
            color: #D4D4D4;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 12px;
            letter-spacing: 2px;
        }
        QPushButton:hover {
            background-color: #2A2A2A;
            border: 1px solid #F97316;
            color: #FAFAFA;
        }
        QPushButton:pressed {
            background-color: #EA580C;
            color: #0A0A0A;
            border: 1px solid #EA580C;
            padding-top: 9px;
            padding-left: 17px;
        }'''
text = text.replace(old_btn_qss, new_btn_qss)

with open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)
