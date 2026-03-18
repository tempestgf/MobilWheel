import sys
import re

kt_path = r"app/src/main/java/com/tempestgf/steeringwheel/DashboardActivity.kt"

with open(kt_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Remove the hide logic for buttons
remove_buttons = r"""\s*// Hide unused manual buttons\s*listOf\(R\.id\.button_left_top.*?findViewById<View>\(id\)\?\.visibility = View\.GONE\s*\}"""
text = re.sub(remove_buttons, "", text, flags=re.DOTALL)

with open(kt_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Removed button references from KT.")
