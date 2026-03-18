# -*- coding: utf-8 -*-
import re

with open('android-client/app/src/main/res/layout/activity_main.xml', 'r', encoding='utf-8') as f:
    xml = f.read()

xml = re.sub(r'<com\.tempestgf\.steeringwheel\.InterceptableFrameLayout.*?</com\.tempestgf\.steeringwheel\.InterceptableFrameLayout>', '', xml, flags=re.DOTALL)
xml = re.sub(r'BOTONES DE ACCI.N.*?(<!-- ={10,}\s+-->\s+<!--\s+CAPA VISUAL HUD)', r'\1', xml, flags=re.DOTALL)

xml = re.sub(r'<LinearLayout[^>]*?id=\"@\+id/centerGearBlock\"[^>]*>.*?<!-- Columna derecha', '<!-- Columna derecha', xml, flags=re.DOTALL) # wait no, I don't want to break it with random regex

xml = xml.replace('tools:context=\".MainActivity\"', 'tools:context=\".DashboardActivity\"')

with open('android-client/app/src/main/res/layout/activity_dashboard.xml', 'w', encoding='utf-8') as f:
    f.write(xml)