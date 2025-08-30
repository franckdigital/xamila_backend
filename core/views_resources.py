from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from .models import ResourceContent
from .serializers import ResourceContentSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_resource_content(request):
    """
    Récupère le contenu actif des ressources (bannière et vidéo YouTube)
    """
    try:
        content = ResourceContent.get_active_content()
        serializer = ResourceContentSerializer(content)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Erreur lors de la récupération du contenu: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
