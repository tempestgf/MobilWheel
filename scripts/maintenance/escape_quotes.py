import io
import os

base_dir = 'android-client/app/src/main/res/'
filepath = os.path.join(base_dir, 'values-ca', 'strings.xml')

with io.open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("mètodes d'entrada", "mètodes d\\'entrada")
text = text.replace("SOBRE L'APP", "SOBRE L\\'APP")
text = text.replace("d'IP manual", "d\\'IP manual")

with io.open(filepath, 'w', encoding='utf-8') as f:
    f.write(text)

filepath_es = os.path.join(base_dir, 'values-es', 'strings.xml')
with io.open(filepath_es, 'r', encoding='utf-8') as f:
    text = f.read()
# Just in case we missed any in es, though none exist
with io.open(filepath_es, 'w', encoding='utf-8') as f:
    f.write(text)

