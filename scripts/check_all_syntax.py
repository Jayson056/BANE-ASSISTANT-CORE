import os
import py_compile
import sys

def check_syntax(directory):
    errors = []
    for root, dirs, files in os.walk(directory):
        if ".venv" in root or "__pycache__" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    py_compile.compile(path, doraise=True)
                except py_compile.PyCompileError as e:
                    errors.append((path, str(e)))
                except PermissionError:
                    pass
    return errors

if __name__ == "__main__":
    cl_dir = "/home/user/BANE_CORE"
    errs = check_syntax(cl_dir)
    if errs:
        print(f"Found {len(errs)} syntax errors:")
        for path, err in errs:
            print(f"--- {path} ---\n{err}\n")
        sys.exit(1)
    else:
        print("✅ No syntax errors found in BANE Python files.")
        sys.exit(0)
