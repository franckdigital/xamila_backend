#!/usr/bin/env python
"""
Script pour ajouter l'endpoint admin de liste des cohortes
"""

# Contenu à ajouter à la fin de views_cohorte.py
ENDPOINT_CODE = '''

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lister_toutes_cohortes(request):
    """
    Liste toutes les cohortes (Admin uniquement)
    """
    try:
        # Vérifier que l'utilisateur est admin
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({
                'message': 'Accès réservé aux administrateurs'
            }, status=status.HTTP_403_FORBIDDEN)
        
        cohortes = Cohorte.objects.all().order_by('-created_at')
        
        cohortes_data = []
        for cohorte in cohortes:
            mois_nom = dict(Cohorte.MOIS_CHOICES)[cohorte.mois]
            cohortes_data.append({
                'id': str(cohorte.id),
                'code': cohorte.code,
                'nom': cohorte.nom,
                'mois': cohorte.mois,
                'mois_nom': mois_nom,
                'annee': cohorte.annee,
                'user_id': cohorte.user_id,
                'email_utilisateur': cohorte.email_utilisateur,
                'username': cohorte.user.username if cohorte.user else None,
                'actif': cohorte.actif,
                'created_at': cohorte.created_at.isoformat()
            })
        
        return Response({
            'cohortes': cohortes_data,
            'count': len(cohortes_data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'message': f'Erreur serveur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
'''

print("=== AJOUT ENDPOINT ADMIN COHORTES ===")
print("1. Ajoutez ce code à la fin de core/views_cohorte.py:")
print(ENDPOINT_CODE)
print("\n2. Ajoutez cette ligne dans core/urls.py:")
print("    path('cohortes/admin/toutes/', views_cohorte.lister_toutes_cohortes, name='lister_toutes_cohortes'),")
