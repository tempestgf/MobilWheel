import re
with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

en_insertion = """'vjoy_prob_title': 'vJoy',
        'speed': 'SPEED km/h',
        'gear': 'GEAR',
        'rpm': 'RPM',
        'accel': 'ACCELERATE',
        'steer': 'STEERING',"""

es_insertion = """'vjoy_prob_title': 'vJoy',
        'speed': 'VELOCIDAD km/h',
        'gear': 'MARCHA',
        'rpm': 'RPM',
        'accel': 'ACELERADOR',
        'steer': 'DIRECCIÓN',"""

ca_insertion = """'vjoy_prob_title': 'vJoy',
        'speed': 'VELOCITAT km/h',
        'gear': 'MARXA',
        'rpm': 'RPM',
        'accel': 'ACCELERADOR',
        'steer': 'DIRECCIÓ',"""

pieces = text.split("'vjoy_prob_title': 'vJoy',")
if len(pieces) == 4:
    text = pieces[0] + en_insertion + pieces[1] + es_insertion + pieces[2] + ca_insertion + pieces[3]

with open('python-server/ServerApp.py', 'w', encoding='utf-8') as f:
    f.write(text)
