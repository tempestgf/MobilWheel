
import sys

def fix_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            text = f.read()
        
        raw_bytes = text.encode("latin1", errors="replace")
        fixed_text = raw_bytes.decode("utf-8")
        
        with open(filepath, "w", encoding="utf-8", newline="\n") as f:
            f.write(fixed_text)
        print(f"Fixed {filepath}")
    except Exception as e:
        print(f"Failed {filepath}: {e}")

for f in ["README.md", "README.es.md", "README.ca.md"]:
    fix_file(f)

