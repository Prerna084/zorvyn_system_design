import os
import re

root_dir = r"c:\Users\shres\Desktop\zorvyn_system_design"
app_dir = os.path.join(root_dir, "app")
src_dir = os.path.join(root_dir, "src")

# 1. Rename app -> src
if os.path.exists(app_dir):
    os.rename(app_dir, src_dir)

# 2. Rename subdirectories
rename_map = {
    "core": "config",
    "dependencies": "middlewares",
    "schemas": "validations"
}
for old_name, new_name in rename_map.items():
    old_path = os.path.join(src_dir, old_name)
    new_path = os.path.join(src_dir, new_name)
    if os.path.exists(old_path):
        os.rename(old_path, new_path)

# 3. Move database.py
old_db_path = os.path.join(src_dir, "database.py")
new_db_path = os.path.join(src_dir, "config", "database.py")
if os.path.exists(old_db_path):
    os.rename(old_db_path, new_db_path)

# 4. Search and Replace in all files
replacements = [
    (r"app\.core", r"src.config"),
    (r"app\.dependencies", r"src.middlewares"),
    (r"app\.schemas", r"src.validations"),
    (r"app\.database", r"src.config.database"),
    (r"app\.", r"src."),
    (r"from src import", r"from src import"),
    (r"src/config", r"src/config"),
    (r"src/middlewares", r"src/middlewares"),
    (r"src/validations", r"src/validations"),
    (r"src/", r"src/"),
]

for folder in [src_dir, os.path.join(root_dir, "tests"), os.path.join(root_dir, "scripts"), root_dir]:
    for root, dirs, files in os.walk(folder):
        # Prevent accessing non-existent test or script dirs if they were renamed
        if ".venv" in root or ".git" in root or "__pycache__" in root or ".pytest_cache" in root:
            continue
        for f in files:
            file_path = os.path.join(root, f)
            if not file_path.endswith('.py') and not file_path.endswith('.md'):
                continue
            
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                
            orig_content = content
            for old_patt, new_patt in replacements:
                content = re.sub(old_patt, new_patt, content)
                
            if content != orig_content:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)

print("done")
