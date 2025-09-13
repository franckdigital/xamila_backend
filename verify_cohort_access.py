#!/usr/bin/env python3
"""
Server-side verification script for cohort access control
Run this directly on the production server to test functionality
"""

# Django setup for standalone script
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/var/www/xamila/xamila_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models import User, Cohorte, SavingsChallenge
from core.utils_cohorte_access import verifier_acces_challenge_actif
from django.http import HttpRequest

def test_cohort_access():
    print("🧪 Verifying Cohort Access Control")
    print("=" * 50)
    
    # Test 1: Check all cohorts
    print("\n📋 Current Cohorts Status:")
    cohorts = Cohorte.objects.all()
    for cohorte in cohorts:
        users_count = User.objects.filter(cohorte=cohorte).count()
        print(f"- {cohorte.nom}: Active={cohorte.actif}, Users={users_count}")
    
    # Test 2: Check demo user
    print("\n👤 Demo User Status:")
    try:
        demo_user = User.objects.get(email='demo@xamila.finance')
        print(f"User: {demo_user.email}")
        print(f"Role: {demo_user.role}")
        
        if hasattr(demo_user, 'cohorte') and demo_user.cohorte:
            print(f"Cohort: {demo_user.cohorte.nom}")
            print(f"Cohort Active: {demo_user.cohorte.actif}")
        else:
            print("No cohort assigned")
            
    except User.DoesNotExist:
        print("Demo user not found")
    
    # Test 3: Test access control function
    print("\n🔒 Access Control Test:")
    try:
        demo_user = User.objects.get(email='demo@xamila.finance')
        request = HttpRequest()
        request.user = demo_user
        request.session = {}
        
        acces_autorise, message = verifier_acces_challenge_actif(request)
        print(f"Access Authorized: {acces_autorise}")
        print(f"Message: {message}")
        
        if acces_autorise:
            print("✅ User has access to savings challenges")
        else:
            print("❌ User access blocked (expected if cohort inactive)")
            
    except Exception as e:
        print(f"Error testing access: {e}")
    
    # Test 4: Check active challenges
    print("\n💰 Active Savings Challenges:")
    challenges = SavingsChallenge.objects.filter(status='ACTIVE')
    print(f"Total active challenges: {challenges.count()}")
    
    print("\n✅ Verification completed!")
    print("If cohort is inactive, access should be blocked - this is correct behavior")

if __name__ == "__main__":
    test_cohort_access()
