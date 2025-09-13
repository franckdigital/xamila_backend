#!/usr/bin/env python3
"""
Simple test to verify cohort access control is working
Tests API endpoints directly from the server
"""

import subprocess
import json

def run_django_command(command):
    """Run a Django management command"""
    try:
        result = subprocess.run(
            f"python manage.py shell -c \"{command}\"",
            shell=True,
            capture_output=True,
            text=True,
            cwd="/var/www/xamila/xamila_backend"
        )
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return None, str(e)

def test_cohort_access_control():
    """Test cohort access control functionality"""
    print("🧪 Testing Cohort Access Control")
    print("=" * 50)
    
    # Test 1: Check if demo user exists and get cohort info
    print("\n🔍 Checking demo user and cohort status...")
    
    check_user_command = """
from core.models import User, Cohorte
from core.utils_cohorte_access import verifier_acces_challenge_actif
from django.http import HttpRequest

try:
    user = User.objects.get(email='demo@xamila.finance')
    print(f'User found: {user.email}')
    print(f'User role: {user.role}')
    
    # Check user's cohort
    if hasattr(user, 'cohorte') and user.cohorte:
        cohorte = user.cohorte
        print(f'User cohort: {cohorte.nom}')
        print(f'Cohort active: {cohorte.actif}')
    else:
        print('User has no cohort assigned')
    
    # Test access verification
    request = HttpRequest()
    request.user = user
    
    acces_autorise, message = verifier_acces_challenge_actif(request)
    print(f'Access authorized: {acces_autorise}')
    print(f'Message: {message}')
    
except User.DoesNotExist:
    print('Demo user not found')
except Exception as e:
    print(f'Error: {e}')
"""
    
    stdout, stderr = run_django_command(check_user_command)
    if stdout:
        print(stdout)
    if stderr:
        print(f"Error: {stderr}")
    
    # Test 2: List all cohorts and their status
    print("\n📋 Listing all cohorts...")
    
    list_cohorts_command = """
from core.models import Cohorte, User

cohorts = Cohorte.objects.all()
print(f'Total cohorts: {cohorts.count()}')

for cohorte in cohorts:
    users_count = User.objects.filter(cohorte=cohorte).count()
    print(f'- {cohorte.nom}: Active={cohorte.actif}, Users={users_count}')
"""
    
    stdout, stderr = run_django_command(list_cohorts_command)
    if stdout:
        print(stdout)
    if stderr:
        print(f"Error: {stderr}")
    
    # Test 3: Test savings challenge access
    print("\n💰 Testing savings challenge access...")
    
    test_challenge_access_command = """
from core.models import User, SavingsChallenge
from core.utils_cohorte_access import verifier_acces_challenge_actif
from django.http import HttpRequest

try:
    user = User.objects.get(email='demo@xamila.finance')
    request = HttpRequest()
    request.user = user
    
    # Test access verification
    acces_autorise, message = verifier_acces_challenge_actif(request)
    
    if acces_autorise:
        challenges = SavingsChallenge.objects.filter(status='ACTIVE')
        print(f'Access granted - {challenges.count()} active challenges available')
    else:
        print(f'Access denied: {message}')
        print('This is expected behavior if cohort is inactive')
    
except Exception as e:
    print(f'Error testing challenge access: {e}')
"""
    
    stdout, stderr = run_django_command(test_challenge_access_command)
    if stdout:
        print(stdout)
    if stderr:
        print(f"Error: {stderr}")
    
    print("\n✅ Cohort access control test completed")
    print("If cohort is inactive, access should be denied - this is correct behavior")

if __name__ == "__main__":
    test_cohort_access_control()
