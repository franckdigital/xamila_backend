#!/usr/bin/env python
"""
Script simple pour tester Ma Caisse sans connexion DB
"""

from datetime import date, timedelta

def test_activation_logic():
    """
    Test la logique d'activation sans base de données
    """
    print("=== TEST LOGIQUE ACTIVATION MA CAISSE ===")
    
    today = date.today()
    print(f"Date d'aujourd'hui: {today}")
    
    # Simuler différents scénarios
    scenarios = [
        ("Objectif créé aujourd'hui", today, today + timedelta(days=21)),
        ("Objectif créé il y a 10 jours", today - timedelta(days=10), today - timedelta(days=10) + timedelta(days=21)),
        ("Objectif créé il y a 25 jours", today - timedelta(days=25), today - timedelta(days=25) + timedelta(days=21)),
        ("Objectif créé il y a 30 jours", today - timedelta(days=30), today - timedelta(days=30) + timedelta(days=21)),
    ]
    
    for nom, date_creation, date_activation in scenarios:
        is_activated = today >= date_activation
        days_remaining = (date_activation - today).days
        
        print(f"\n{nom}:")
        print(f"  - Créé le: {date_creation}")
        print(f"  - Activation le: {date_activation}")
        print(f"  - Activé: {is_activated}")
        print(f"  - Jours restants: {days_remaining}")

if __name__ == '__main__':
    test_activation_logic()
