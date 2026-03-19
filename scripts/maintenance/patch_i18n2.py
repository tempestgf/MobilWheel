import sys, re
with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

# I18N additions
import ast
match = re.search(r'I18N = (\{.*?\n\})', text, re.DOTALL)
if match:
    # We will do some textual inserts safely instead of full AST eval since it's large and formatting might get lost.
    pass

# English additions
text = text.replace("'vjoy_prob_title': 'vJoy',", "'vjoy_prob_title': 'vJoy',\n        'speed': 'SPEED km/h',\n        'gear': 'GEAR',\n        'rpm': 'RPM',\n        'accel': 'ACCELERATE',\n        'steer': 'STEERING',")
# Spanish additions
text = text.replace("'vjoy_prob_title': 'vJoy',", "'vjoy_prob_title': 'vJoy',\n        'speed': 'VELOCIDAD km/h',\n        'gear': 'MARCHA',\n        'rpm': 'RPM',\n        'accel': 'ACELERADOR',\n        'steer': 'DIRECCIÓN',", 1)  # Only first is EN, wait, better use exact string matching.
