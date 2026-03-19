import sys
with open('python-server/ServerApp.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace Spanish ones correctly
text = text.replace(
    "'vjoy_prob_title': 'vJoy',\n        'speed': 'SPEED km/h',\n        'gear': 'GEAR',\n        'rpm': 'RPM',\n        'accel': 'ACCELERATE',\n        'steer': 'STEERING',",
    "'vjoy_prob_title': 'vJoy',\n        'speed': 'VELOCIDAD km/h',\n        'gear': 'MARCHA',\n        'rpm': 'RPM',\n        'accel': 'ACELERADOR',\n        'steer': 'DIRECCIÓN',",
    1 # Second occurence, wait, it replaced all 3 initially.
)
