"""
Script de test pour vérifier les routes SGI Manager
"""
import sys
import os
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from django.urls import resolve, reverse
from core import views_sgi_manager

def test_routes():
    """Teste si les routes SGI Manager sont correctement configurées"""
    
    print("=" * 60)
    print("TEST DES ROUTES SGI MANAGER")
    print("=" * 60)
    
    routes_to_test = [
        ('sgi_manager_list', 'GET /api/sgis/manager/list/', None),
        ('sgi_manager_create', 'POST /api/sgis/manager/create/', None),
        ('sgi_manager_update', 'PATCH /api/sgis/manager/update/<uuid>/', {'sgi_id': '12345678-1234-5678-1234-567812345678'}),
        ('sgi_manager_delete', 'DELETE /api/sgis/manager/delete/<uuid>/', {'sgi_id': '12345678-1234-5678-1234-567812345678'}),
        ('sgi_manager_mine', 'GET /api/sgis/manager/mine/', None),
    ]
    
    print("\n1. Test de résolution des routes par nom:")
    print("-" * 60)
    for route_name, description, kwargs in routes_to_test:
        try:
            if kwargs:
                url = reverse(route_name, kwargs=kwargs)
            else:
                url = reverse(route_name)
            print(f"✅ {route_name:25} -> {url}")
        except Exception as e:
            print(f"❌ {route_name:25} -> ERREUR: {str(e)}")
    
    print("\n2. Test de résolution des URLs:")
    print("-" * 60)
    test_urls = [
        '/api/sgis/manager/list/',
        '/api/sgis/manager/create/',
        '/api/sgis/manager/update/12345678-1234-5678-1234-567812345678/',
        '/api/sgis/manager/delete/12345678-1234-5678-1234-567812345678/',
        '/api/sgis/manager/mine/',
    ]
    
    for url in test_urls:
        try:
            match = resolve(url)
            print(f"✅ {url:70} -> {match.func.__name__}")
        except Exception as e:
            print(f"❌ {url:70} -> ERREUR: {str(e)}")
    
    print("\n3. Vérification des vues:")
    print("-" * 60)
    views_to_check = [
        ('AllSGIsListView', views_sgi_manager.AllSGIsListView),
        ('SGICreateForManagerView', views_sgi_manager.SGICreateForManagerView),
        ('SGIUpdateView', views_sgi_manager.SGIUpdateView),
        ('SGIDeleteView', views_sgi_manager.SGIDeleteView),
        ('MySGIView', views_sgi_manager.MySGIView),
    ]
    
    for view_name, view_class in views_to_check:
        try:
            if hasattr(view_class, 'as_view'):
                print(f"✅ {view_name:30} -> Classe APIView valide")
            else:
                print(f"❌ {view_name:30} -> Pas une APIView")
        except Exception as e:
            print(f"❌ {view_name:30} -> ERREUR: {str(e)}")
    
    print("\n4. Test des méthodes HTTP:")
    print("-" * 60)
    
    # Test SGIUpdateView
    try:
        update_view = views_sgi_manager.SGIUpdateView()
        if hasattr(update_view, 'patch'):
            print(f"✅ SGIUpdateView.patch          -> Méthode PATCH disponible")
        else:
            print(f"❌ SGIUpdateView.patch          -> Méthode PATCH manquante")
    except Exception as e:
        print(f"❌ SGIUpdateView                -> ERREUR: {str(e)}")
    
    # Test SGIDeleteView
    try:
        delete_view = views_sgi_manager.SGIDeleteView()
        if hasattr(delete_view, 'delete'):
            print(f"✅ SGIDeleteView.delete         -> Méthode DELETE disponible")
        else:
            print(f"❌ SGIDeleteView.delete         -> Méthode DELETE manquante")
    except Exception as e:
        print(f"❌ SGIDeleteView                -> ERREUR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("TEST TERMINÉ")
    print("=" * 60)
    print("\nSi toutes les routes sont ✅, le problème vient probablement de:")
    print("1. Le serveur backend n'est pas redémarré")
    print("2. L'URL frontend ne correspond pas exactement")
    print("3. Le token d'authentification est invalide")
    print("4. L'ID de la SGI n'existe pas")
    print("\nCommandes pour redémarrer le serveur:")
    print("  cd xamila_backend")
    print("  python manage.py runserver")

if __name__ == '__main__':
    test_routes()
