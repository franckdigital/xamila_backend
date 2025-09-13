#!/usr/bin/env python3
"""
Deploy import fix for views_cohortes.py
"""

import subprocess
import sys

def run_ssh_command(command, description):
    """Execute SSH command and return result"""
    print(f"\n=== {description} ===")
    try:
        full_command = f"ssh root@xamila.finance '{command}'"
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True, timeout=30)
        
        print(f"Command: {command}")
        print(f"Exit code: {result.returncode}")
        if result.stdout.strip():
            print(f"Output:\n{result.stdout.strip()}")
        if result.stderr.strip():
            print(f"Error:\n{result.stderr.strip()}")
        
        return result.returncode == 0
    except Exception as e:
        print(f"Exception: {e}")
        return False

def main():
    """Deploy import fix and restart server"""
    print("=== DEPLOYING IMPORT FIX ===")
    
    # 1. Pull latest changes from GitHub
    if not run_ssh_command("cd /var/www/xamila_backend && git pull origin main", "Git Pull"):
        print("Failed to pull changes")
        return False
    
    # 2. Restart Django service
    if not run_ssh_command("systemctl restart xamila", "Restart Django Service"):
        print("Failed to restart service")
        return False
    
    # 3. Wait a moment for service to start
    run_ssh_command("sleep 5", "Wait for service startup")
    
    # 4. Check service status
    run_ssh_command("systemctl status xamila --no-pager", "Check Service Status")
    
    # 5. Test API endpoint
    run_ssh_command("curl -I http://localhost:8000/health/", "Test Local API")
    
    # 6. Test external API
    run_ssh_command("curl -I https://api.xamila.finance/health/", "Test External API")
    
    print("\n=== DEPLOYMENT COMPLETE ===")
    return True

if __name__ == "__main__":
    main()
