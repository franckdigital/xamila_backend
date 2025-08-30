from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from .models import ResourceContent
from .serializers import ResourceContentSerializer

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_resource_content(request):
    """
    Met à jour le contenu des ressources (bannière et vidéo YouTube)
    Accessible uniquement aux administrateurs
    """
    try:
        # Vérifier que l'utilisateur est admin
        if not request.user.is_staff and request.user.role != 'ADMIN':
            return Response({
                'success': False,
                'message': 'Accès non autorisé. Seuls les administrateurs peuvent modifier les ressources.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Récupérer ou créer le contenu actif
        content = ResourceContent.get_active_content()
        
        # Mettre à jour avec les nouvelles données
        serializer = ResourceContentSerializer(content, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            return Response({
                'success': True,
                'message': 'Contenu des ressources mis à jour avec succès',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Données invalides',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Erreur lors de la mise à jour: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_admin_resource_content(request):
    """
    Récupère le contenu des ressources pour l'administration
    """
    try:
        # Vérifier que l'utilisateur est admin
        if not request.user.is_staff and request.user.role != 'ADMIN':
            return Response({
                'success': False,
                'message': 'Accès non autorisé.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        content = ResourceContent.get_active_content()
        serializer = ResourceContentSerializer(content)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Erreur lors de la récupération: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
