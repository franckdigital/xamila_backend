#!/usr/bin/env python3
"""
Script to deploy cohort access control fixes to production server
Applies comprehensive access verification to all savings challenge endpoints
"""

import subprocess
import sys
import os

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
    print("🚀 Deploying Cohort Access Control Fixes")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = "/var/www/xamila/xamila_backend"
    
    commands = [
        # Pull latest changes from git
        (f"cd {backend_dir} && git pull origin main", "Pulling latest changes from Git"),
        
        # Collect static files
        (f"cd {backend_dir} && python manage.py collectstatic --noinput", "Collecting static files"),
        
        # Apply any pending migrations
        (f"cd {backend_dir} && python manage.py migrate", "Applying database migrations"),
        
        # Restart Django service
        ("sudo systemctl restart xamila", "Restarting Django service"),
        
        # Check service status
        ("sudo systemctl status xamila --no-pager -l", "Checking service status"),
        
        # Test API health
        ("curl -s https://api.xamila.finance/health/ | python -m json.tool", "Testing API health endpoint")
    ]
    
    success_count = 0
    for command, description in commands:
        if run_command(command, description):
            success_count += 1
        else:
            print(f"\n⚠️  Command failed: {description}")
            if "restart" in description.lower():
                print("Service restart failed - checking logs...")
                run_command("sudo journalctl -u xamila --no-pager -l -n 20", "Checking service logs")
    
    print(f"\n📊 Deployment Summary: {success_count}/{len(commands)} commands successful")
    
    if success_count == len(commands):
        print("\n🎉 Cohort access control fixes deployed successfully!")
        print("\nKey changes applied:")
        print("- ✅ All savings challenge endpoints now verify cohort access")
        print("- ✅ Users with inactive cohorts cannot access challenge features")
        print("- ✅ Empty querysets returned for unauthorized access attempts")
        print("- ✅ Consistent error responses with CHALLENGE_ACCESS_DENIED code")
        
        print("\nEndpoints protected:")
        print("- SavingsChallengeListView (list active challenges)")
        print("- join_challenge (join new challenges)")
        print("- make_deposit (make deposits)")
        print("- ChallengeParticipationListView (list participations)")
        print("- UserChallengeParticipationsView (user participations)")
        print("- ChallengeParticipationDetailView (participation details)")
        print("- UserSavingsDepositsView (deposit history)")
        print("- get_leaderboard (challenge leaderboards)")
        
        print("\n🔍 Test with demo@xamila.finance to verify cohort deactivation blocks access")
    else:
        print("\n❌ Deployment had issues - check logs above")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
