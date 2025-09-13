#!/usr/bin/env python3
"""
Deploy the corrected cohort access control fixes
"""

import subprocess
import sys

def run_command(command, description):
    """Execute a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Deploying Corrected Cohort Access Control")
    print("=" * 50)
    
    backend_dir = "/var/www/xamila/xamila_backend"
    
    commands = [
        # Collect static files
        (f"cd {backend_dir} && python manage.py collectstatic --noinput", "Collecting static files"),
        
        # Restart Django service
        ("sudo systemctl restart xamila", "Restarting Django service"),
        
        # Check service status
        ("sudo systemctl status xamila --no-pager -l", "Checking service status"),
    ]
    
    success_count = 0
    for command, description in commands:
        if run_command(command, description):
            success_count += 1
    
    print(f"\n📊 Deployment Summary: {success_count}/{len(commands)} commands successful")
    
    if success_count == len(commands):
        print("\n🎉 Corrected cohort access control deployed successfully!")
        print("\nKey fixes applied:")
        print("- ✅ Fixed cohortes relationship (plural) in access verification")
        print("- ✅ Added session initialization for test compatibility")
        print("- ✅ Updated to handle many-to-many cohort relationships")
        print("- ✅ Improved error handling and messaging")
    else:
        print("\n❌ Deployment had issues - check logs above")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
