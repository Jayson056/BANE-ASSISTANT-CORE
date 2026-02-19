
import os
import sys

# Experimenting Payload for BANE Sandbox
# This script tests the isolation of the AI Sandbox environment.

def run_experiment():
    print("--- 🛡️ BANE SANDBOX EXPERIMENT START ---")
    
    # 1. Access inside Sandbox (Authorized)
    print("\n[STEP 1] Testing internal storage access...")
    try:
        # Get directory where script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_file = os.path.join(current_dir, "sandbox_test.txt")
        with open(test_file, "w") as f:
            f.write("Sandbox test data")
        print(f"✅ Success: Can write to {test_file}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 2. Access outside Sandbox (Unauthorized)
    print("\n[STEP 2] Testing external file access (should fail if blocked)...")
    try:
        # Trying to read the main BANE config or a system file
        with open("/home/user/BANE_CORE/main.py", "r") as f:
            content = f.read(20)
            print(f"❗ Alert: Can read outside files! Content: {content}...")
    except Exception as e:
        print(f"🛡️ Blocked: Cannot read outside files as expected. ({type(e).__name__})")

    # 3. System Commands (Identity Check)
    print("\n[STEP 3] Testing system command execution...")
    try:
        res = os.popen("whoami").read().strip()
        print(f"⚠️ Identity: whoami -> {res}")
        
        proc_list = os.popen("ps -e | head -n 5").read().strip()
        print(f"⚠️ Process View (Top 5):\n{proc_list}")
    except Exception as e:
        print(f"🛡️ Blocked: System command execution failed. ({type(e).__name__})")

    # 4. Network Probe (Simulated)
    print("\n[STEP 4] Simulating network probe...")
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        # Try to connect to BANE dashboard locally
        result = s.connect_ex(('127.0.0.1', 8081))
        if result == 0:
            print("⚠️ Result: Port 8081 is OPEN (Internal LAN reachable)")
        else:
            print("🛡️ Result: Port 8081 filtered/closed.")
        s.close()
    except Exception as e:
        print(f"🛡️ Blocked: Network access failed. ({e})")

    print("\n--- EXPERIMENT COMPLETE ---")

if __name__ == "__main__":
    run_experiment()
