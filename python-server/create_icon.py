#!/usr/bin/env python
from PIL import Image
import os

# Abrir PNG
img = Image.open('app_logo.png')
print(f"Original image: {img.size}, mode: {img.mode}")

# Redimensionar a 256x256
img_ico = img.resize((256, 256), Image.Resampling.LANCZOS)

# Convertir a RGB si tiene alpha
if img_ico.mode == 'RGBA':
    background = Image.new('RGB', img_ico.size, (255, 255, 255))
    background.paste(img_ico, mask=img_ico.split()[3])
    img_ico = background
else:
    img_ico = img_ico.convert('RGB')

# Guardar como ICO
img_ico.save('app_logo.ico', 'ICO')

print('app_logo.ico created successfully')
print('File size:', os.path.getsize('app_logo.ico'), 'bytes')


