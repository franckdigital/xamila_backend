from rest_framework import serializers
from .models_permissions import Permission, RolePermission

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'code', 'category', 'description', 'is_active']

class RolePermissionSerializer(serializers.ModelSerializer):
    permission = PermissionSerializer(read_only=True)
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    permission_code = serializers.CharField(source='permission.code', read_only=True)
    permission_category = serializers.CharField(source='permission.category', read_only=True)
    
    class Meta:
        model = RolePermission
        fields = [
            'id', 'role', 'is_granted', 'created_at', 'updated_at',
            'permission', 'permission_name', 'permission_code', 'permission_category'
        ]
