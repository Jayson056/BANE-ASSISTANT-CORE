import os

# Header to add
HEADER_PY = """# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
"""

HEADER_SH = """# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
"""

def add_headers(directory):
    count = 0
    # Folders to completely skip
    skip_dirs = {'.venv', '.git', '__pycache__', 'storage', 'Debug', '.antigravity'}
    
    for root, dirs, files in os.walk(directory):
        # Filter out skipped directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            path = os.path.join(root, file)
            header = None
            
            if file.endswith('.py'):
                header = HEADER_PY
            elif file.endswith('.sh'):
                header = HEADER_SH
            
            if header:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if header already exists (case insensitive check for 'Copyright')
                    if "Copyright" in content[:200] or "Created by Jayson056" in content[:200]:
                        continue
                    
                    # Add header. If it's a shell script with #!, insert after shebang
                    new_content = ""
                    if file.endswith('.sh') and content.startswith('#!'):
                        lines = content.split('\n')
                        shebang = lines[0]
                        remaining = '\n'.join(lines[1:])
                        new_content = f"{shebang}\n{header}{remaining}"
                    else:
                        new_content = f"{header}{content}"
                    
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"✅ Added header to: {path}")
                    count += 1
                except Exception as e:
                    print(f"❌ Error processing {path}: {e}")
    
    return count

if __name__ == "__main__":
    total = add_headers("/home/user/BANE_CORE")
    print(f"\n✨ Successfully updated {total} files.")
