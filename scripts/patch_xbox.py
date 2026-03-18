import re

path_xbox = 'C:/Users/Tempestgf/Coding/MobileWheel/python-server/xbox.py'
with open(path_xbox, 'r', encoding='utf-8') as f:
    text = f.read()

# Only replace if T: is still in there
if '"T:{speed}:{gear}:{rpm}\\n"' in text:
    replacement = """                speed = int(data.speed_kmh)
                gear = data.gear + 1  # Volver al formato original
                rpm = int(data.rpms)

                try:
                    import json, dataclasses
                    if hasattr(data, "to_json_payload"):
                        t_dict = data.to_json_payload()
                    elif dataclasses.is_dataclass(data):
                        t_dict = dataclasses.asdict(data)
                    else:
                        t_dict = {"speed": speed, "gear": gear, "rpm": rpm}
                except:
                    t_dict = {"speed": speed, "gear": gear, "rpm": rpm}

                t_dict["speed"] = speed
                t_dict["gear"] = gear
                t_dict["rpm"] = rpm

                msg = f"J:{json.dumps(t_dict)}\\n\""""
    text = re.sub(r'speed = int\(data\.speed_kmh\)\s+gear = data\.gear \+ 1.*?msg = f"T:\{speed\}:\{gear\}:\{rpm\}\\n"', replacement, text, flags=re.DOTALL)
    
    with open(path_xbox, 'w', encoding='utf-8') as f:
        f.write(text)
    print("xbox.py patched with JSON output")
else:
    print("xbox.py already patched or pattern not found at", path_xbox)


# ALSO check the other xbox.py just in case
path_xbox_so = 'C:/Users/Tempestgf/Coding/Desktop/smoothoperator/mobilewheel/xbox.py'
try:
    with open(path_xbox_so, 'r', encoding='utf-8') as f:
        text_so = f.read()
    if '"T:{speed}:{gear}:{rpm}\\n"' in text_so:
        text_so = re.sub(r'speed = int\(data\.speed_kmh\)\s+gear = data\.gear \+ 1.*?msg = f"T:\{speed\}:\{gear\}:\{rpm\}\\n"', replacement, text_so, flags=re.DOTALL)
        with open(path_xbox_so, 'w', encoding='utf-8') as f:
            f.write(text_so)
        print("Smoothoperator xbox.py patched with JSON output")
        
except Exception as e:
    print("Could not do so", e)
