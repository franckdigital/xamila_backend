from rest_framework import serializers
from .models_bilans import FluxFinancier, BilanFinancier
from datetime import datetime, date

class FluxFinancierSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = FluxFinancier
        fields = [
            'id', 'date', 'type', 'type_display', 'categorie', 
            'description', 'montant', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Ajouter automatiquement l'utilisateur connecté
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class BilanFinancierSerializer(serializers.ModelSerializer):
    flux_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BilanFinancier
        fields = [
            'id', 'periode_debut', 'periode_fin', 'total_revenus', 
            'total_depenses', 'solde', 'suggestions_generees', 
            'flux_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_flux_count(self, obj):
        return FluxFinancier.objects.filter(
            user=obj.user,
            date__gte=obj.periode_debut,
            date__lte=obj.periode_fin
        ).count()

class BilanCalculeSerializer(serializers.Serializer):
    """Serializer pour les données de bilan calculées dynamiquement"""
    total_revenus = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_depenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    solde = serializers.DecimalField(max_digits=12, decimal_places=2)
    suggestions = serializers.ListField(child=serializers.DictField(), required=False)
    flux_par_categorie = serializers.DictField(required=False)
    periode_debut = serializers.DateField(required=False)
    periode_fin = serializers.DateField(required=False)
