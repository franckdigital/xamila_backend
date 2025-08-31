#!/usr/bin/env python
"""
Script pour résoudre le conflit de migration sur le serveur de production
"""

print("=== Instructions pour résoudre le conflit de migration ===")
print()
print("1. Supprimer la migration problématique:")
print("   rm /var/www/xamila/xamila_backend/core/migrations/0005_add_and_fix_caisse_activation.py")
print()
print("2. Modifier la migration 0006_fix_caisse_activation.py pour qu'elle dépende de 0009:")
print("   Changer la dépendance de ('core', '0005_add_and_fix_caisse_activation') vers ('core', '0009_savingsgoal_date_activation_caisse')")
print()
print("3. Ou plus simple: supprimer complètement 0006_fix_caisse_activation.py et utiliser seulement la commande de gestion:")
print("   rm /var/www/xamila/xamila_backend/core/migrations/0006_fix_caisse_activation.py")
print()
print("4. Appliquer les migrations restantes:")
print("   python manage.py migrate")
print()
print("5. Exécuter la commande de correction des données:")
print("   python manage.py fix_caisse_activation")
print()
print("=== Commandes à exécuter sur le serveur ===")
print("rm /var/www/xamila/xamila_backend/core/migrations/0005_add_and_fix_caisse_activation.py")
print("rm /var/www/xamila/xamila_backend/core/migrations/0006_fix_caisse_activation.py")
print("python manage.py migrate")
print("python manage.py fix_caisse_activation")
