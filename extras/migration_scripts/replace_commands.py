import os
import re
from pathlib import Path

target_exts = {".py", ".md", ".toml", ".txt", ".in"}
excludes = {"venv", ".venv", ".git", "dist", "guardrag.egg-info", ".pytest_cache"}

workdir = Path("C:/Users/Asus/Downloads/GUARD-RAG-main")

for path in workdir.rglob("*"):
    if path.is_file() and path.suffix in target_exts:
        # Skip excluded dirs
        if any(ex in path.parts for ex in excludes):
            continue
            
        try:
            content = path.read_text(encoding="utf-8")
            changed = False
            
            # 1. pip install guard-rag -> pip install guard-rag
            if "pip install guard-rag" in content:
                content = content.replace("pip install guard-rag", "pip install guard-rag")
                changed = True
                
            # 2. guard-rag --pdf -> guard-rag --pdf  (or any flag)
            if re.search(r'\bguardrag\s+--', content):
                content = re.sub(r'\bguardrag(\s+--)', r'guard-rag\1', content)
                changed = True
                
            # 3. Just solitary `guardrag` CLI example (like when launching GUI)
            if re.search(r'^\s*guardrag\s*$', content, re.MULTILINE):
                content = re.sub(r'(^\s*)guardrag(\s*$)', r'\1guard-rag\2', content, flags=re.MULTILINE)
                changed = True
                
            if changed:
                path.write_text(content, encoding="utf-8")
                print(f"Updated script aliases in: {path.relative_to(workdir)}")
                
        except Exception as e:
            print(f"Skipped {path.name}: {e}")

print("Done updating terminal commands to guard-rag.")
