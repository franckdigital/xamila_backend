from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models_permissions import Permission, RolePermission
from .serializers_permissions import PermissionSerializer, RolePermissionSerializer
from .permissions import IsAdminUser

User = get_user_model()

class UserPermissionsView(generics.ListAPIView):
    """
    Récupère les permissions d'un utilisateur basées sur son rôle
    GET /api/user/permissions/
    """
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Récupérer les permissions accordées pour le rôle de l'utilisateur
        role_permissions = RolePermission.objects.filter(
            role=user.role,
            is_granted=True
        ).select_related('permission')
        
        # Extraire les permissions
        permissions = [rp.permission for rp in role_permissions]
        return permissions

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_permission(request, permission_code):
    """
    Vérifie si l'utilisateur a une permission spécifique
    GET /api/user/permissions/check/{permission_code}/
    """
    user = request.user
    
    try:
        # Vérifier si la permission existe et est accordée pour ce rôle
        role_permission = RolePermission.objects.get(
            role=user.role,
            permission__code=permission_code,
            is_granted=True
        )
        return Response({'has_permission': True})
    except RolePermission.DoesNotExist:
        return Response({'has_permission': False})

class RolePermissionsManagementView(generics.ListAPIView):
    """
    Gestion des permissions par rôle (Admin uniquement)
    GET /api/admin/role-permissions/
    """
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        role = self.request.query_params.get('role')
        if role:
            return RolePermission.objects.filter(role=role).select_related('permission')
        return RolePermission.objects.all().select_related('permission')

@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_role_permission(request):
    """
    Met à jour une permission pour un rôle spécifique
    """
    try:
        role = request.data.get('role')
        permission_code = request.data.get('permission_code')
        is_granted = request.data.get('is_granted', False)
        
        if not role or not permission_code:
            return Response({
                'error': 'Role et permission_code sont requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Récupérer la permission
        try:
            permission = Permission.objects.get(code=permission_code)
        except Permission.DoesNotExist:
            return Response({
                'error': 'Permission non trouvée'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Créer ou mettre à jour la permission de rôle
        role_permission, created = RolePermission.objects.get_or_create(
            role=role,
            permission=permission,
            defaults={'is_granted': is_granted}
        )
        
        if not created:
            role_permission.is_granted = is_granted
            role_permission.save()
        
        return Response({
            'message': f'Permission {"accordée" if is_granted else "révoquée"} avec succès',
            'role': role,
            'permission_code': permission_code,
            'is_granted': is_granted
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_update_role_permission(request):
    """
    Alias pour update_role_permission pour compatibilité avec les URLs
    """
    return update_role_permission(request)
