# BANE - Security Test Script
# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
from core.security import is_allowed_path, check_core_integrity, is_maintenance_mode
import os

def test_security():
    print("🧪 Running Security Tests...")
    
    # 1. Test Core Integrity
    is_safe = check_core_integrity()
    print(f"Checking Integrity: {'SAFE (Read-Only)' if is_safe else 'UNSAFE (Writable)'}")
    
    # 2. Test Path Validation
    test_paths = [
        ("/home/user/BANE_CORE_Workspaces/my_app/test.py", True),  # Allowed workspace
        ("/home/user/BANE_CORE/main.py", False),                # Core file (blocked)
        ("/home/user/BANE_CORE/core/router.py", False),          # Core dir (blocked)
        ("/tmp/some_log.txt", True),                           # Temp (allowed)
        ("/home/user/BANE_CORE/storage/test.png", True),         # Storage (allowed)
        ("/etc/passwd", False),                               # System (blocked)
    ]
    
    print("\nValidating Path Policies:")
    all_passed = True
    for path, expected in test_paths:
        result = is_allowed_path(path)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"  [{status}] {path} -> {result}")
        if result != expected:
            all_passed = False
            
    # 3. Test Maintenance Mode
    print("\nTesting Maintenance Mode:")
    m_file = "/home/user/BANE_CORE/.maintenance"
    try:
        open(m_file, 'a').close()
        print(f"  Maintenance mode ON: {is_maintenance_mode()} (Expected: True)")
        print(f"  Path /home/user/BANE_CORE/main.py allowed? {is_allowed_path('/home/user/BANE_CORE/main.py')} (Expected: True)")
        os.remove(m_file)
        print(f"  Maintenance mode OFF: {is_maintenance_mode()} (Expected: False)")
    except Exception as e:
        print(f"  Failed to test maintenance mode: {e}")

    if all_passed:
        print("\n✨ ALL SECURITY TESTS PASSED!")
    else:
        print("\n🚨 SOME TESTS FAILED!")

if __name__ == "__main__":
    test_security()
