# -*- coding: utf-8 -*-
import io
import os

base_dir = 'android-client/app/src/main/res/'
filepath = os.path.join(base_dir, 'values-ca', 'strings.xml')

with io.open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

# very simply escape all ' inside text nodes (assuming they're inside <string>...</string>)
# actually I can just do text.replace("'", "\\'")
# Wait, replacing all ' could escape existing attributes like name='app_name' but they use double quotes name="app_name"!
text = text.replace("'", "\\'")

with io.open(filepath, 'w', encoding='utf-8') as f:
    f.write(text)
