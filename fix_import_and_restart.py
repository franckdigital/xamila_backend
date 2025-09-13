#!/usr/bin/env python3
"""
Fix import error and restart Django server
"""

import subprocess

def main():
    print("Fixing import error in views_cohortes.py...")
    
    # Commands to execute on server
    commands = [
        # Fix the import in views_cohortes.py
        "cd /var/www/xamila_backend && sed -i 's/from \\.models\\.cohorte import Cohorte/from .models import Cohorte/' core/views_cohortes.py",
        
        # Restart the service
        "systemctl restart xamila",
        
        # Wait for startup
        "sleep 5",
        
        # Check status
        "systemctl status xamila --no-pager -l",
        
        # Test endpoint
        "curl -I http://localhost:8000/health/"
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n{i}. {cmd}")
        try:
            result = subprocess.run(f"ssh root@xamila.finance '{cmd}'", shell=True, capture_output=True, text=True, timeout=30)
            print(f"Exit code: {result.returncode}")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
            if result.stderr:
                print(f"Error: {result.stderr.strip()}")
        except Exception as e:
            print(f"Exception: {e}")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
