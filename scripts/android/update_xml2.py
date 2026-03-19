import sys
import re

xml_path = r"C:\Users\Tempestgf\Coding\MobileWheel\android-client\app\src\main\res\layout\activity_dashboard.xml"

with open(xml_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Match the interactive zones and buttons layout we saw and just remove it.
# It seems there's a big block like:
# <!-- Botones Táctiles Opcionales ... -->
# Let's see if we can find specific nodes. To do it safely, let's use regex to remove any Button nodes, or just the transparent backgrounds.
# Since it's pure racing dashboard, we should strip <Button> tags.

# Actually, I can use an XML parser, but xml.etree drops namespaces. Let's just do regex matching for the containers or buttons.
text = re.sub(r'<Button[^>]*>(?:.*?</Button>)?', '', text, flags=re.DOTALL)
text = re.sub(r'<com\.tempestgf\.steeringwheel\.InterceptableFrameLayout[^>]*>(?:.*?</com\.tempestgf\.steeringwheel\.InterceptableFrameLayout>)?', '', text, flags=re.DOTALL)

with open(xml_path, 'w', encoding='utf-8') as f:
    f.write(text)
    
print("Removed buttons and interceptable layouts.")
