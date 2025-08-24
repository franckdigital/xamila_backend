#!/usr/bin/env python
"""
Test simple pour identifier le problème d'encodage dans challenges
"""

import os
import sys
import django
import requests

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models import User
from core.models_savings_challenge import SavingsChallenge, ChallengeParticipation

def test_challenges_data():
    """Tester les données des challenges directement"""
    
    print("=== TEST CHALLENGES DATA ===")
    
    try:
        user = User.objects.get(email="test@xamila.com")
        print(f"User found: {user.email}")
        
        # Récupérer les participations
        participations = ChallengeParticipation.objects.filter(user=user)
        print(f"Participations found: {participations.count()}")
        
        for participation in participations:
            challenge = participation.challenge
            print(f"\nChallenge: {challenge.id}")
            print(f"  Title: {repr(challenge.title)}")
            print(f"  Description: {repr(challenge.description)}")
            print(f"  Type: {repr(challenge.challenge_type)}")
            print(f"  Category: {repr(challenge.category)}")
            
            # Tester la sérialisation
            try:
                data = {
                    'title': str(challenge.title),
                    'description': str(challenge.description),
                    'type': str(challenge.challenge_type),
                    'category': str(challenge.category)
                }
                print(f"  Serialization: OK")
            except Exception as e:
                print(f"  Serialization ERROR: {str(e)}")
        
        # Test API direct
        print(f"\n=== TEST API DIRECT ===")
        response = requests.get("http://127.0.0.1:8000/api/dashboard/savings/challenges/")
        print(f"API Status: {response.status_code}")
        if response.status_code != 200:
            print(f"API Error: {response.text[:500]}")
        else:
            print("API Success!")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_challenges_data()
