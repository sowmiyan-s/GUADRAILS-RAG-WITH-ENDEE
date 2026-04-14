import os
from pathlib import Path

target_exts = {".py", ".md", ".toml", ".txt", ".in"}
excludes = {"venv", ".venv", ".git", "dist", "guardrag.egg-info", "guardrag.egg-info", ".pytest_cache"}

workdir = Path("C:/Users/Asus/Downloads/GUARD-RAG-main")

for path in workdir.rglob("*"):
    if path.is_file() and path.suffix in target_exts:
        # Skip excluded dirs
        if any(ex in path.parts for ex in excludes):
            continue
            
        try:
            content = path.read_text(encoding="utf-8")
            if "guardrag" in content or "GuardRAG" in content:
                new_content = content.replace("guardrag", "guardrag")
                new_content = new_content.replace("GuardRAG", "GuardRAG")
                path.write_text(new_content, encoding="utf-8")
                print(f"Updated: {path.relative_to(workdir)}")
        except Exception as e:
            print(f"Skipped {path.name}: {e}")

print("Done replacing guardrag with guardrag.")
