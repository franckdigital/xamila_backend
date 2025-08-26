from rest_framework import serializers
from .models_dashboard import UserInvestment, UserSavingsProgress, DashboardTransaction, UserDashboardStats
from .models_savings_challenge import SavingsChallenge
from .models import SGI

class UserInvestmentSerializer(serializers.ModelSerializer):
    sgi_name = serializers.CharField(source='sgi.name', read_only=True)
    sgi_type = serializers.CharField(source='sgi.investment_type', read_only=True)
    performance_percentage = serializers.SerializerMethodField()
    profit_loss = serializers.SerializerMethodField()
    
    class Meta:
        model = UserInvestment
        fields = [
            'id', 'invested_amount', 'current_value', 'purchase_date',
            'is_active', 'sgi_name', 'sgi_type', 'performance_percentage', 
            'profit_loss', 'created_at', 'updated_at'
        ]
    
    def get_performance_percentage(self, obj):
        return obj.performance_percentage
    
    def get_profit_loss(self, obj):
        return obj.profit_loss

class SavingsChallengeSerializer(serializers.ModelSerializer):
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = SavingsChallenge
        fields = [
            'id', 'title', 'description', 'start_date', 'end_date',
            'target_amount', 'is_active', 'days_remaining', 'created_at'
        ]
    
    def get_days_remaining(self, obj):
        from django.utils import timezone
        if obj.end_date > timezone.now():
            return (obj.end_date - timezone.now()).days
        return 0

class UserSavingsProgressSerializer(serializers.ModelSerializer):
    challenge = SavingsChallengeSerializer(read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSavingsProgress
        fields = [
            'id', 'challenge', 'current_amount', 'streak_days',
            'last_saving_date', 'badges_earned', 'progress_percentage',
            'rank', 'created_at', 'updated_at'
        ]
    
    def get_progress_percentage(self, obj):
        return obj.progress_percentage
    
    def get_rank(self, obj):
        return obj.rank

class DashboardTransactionSerializer(serializers.ModelSerializer):
    sgi_name = serializers.CharField(source='sgi.name', read_only=True)
    challenge_title = serializers.CharField(source='savings_challenge.title', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = DashboardTransaction
        fields = [
            'id', 'transaction_type', 'transaction_type_display', 'amount',
            'status', 'status_display', 'description', 'reference_id',
            'sgi_name', 'challenge_title', 'created_at', 'updated_at',
            'processed_at'
        ]

class UserDashboardStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDashboardStats
        fields = [
            'id', 'total_portfolio_value', 'total_invested_amount',
            'global_performance_percentage', 'current_month_savings',
            'savings_rank', 'total_savings', 'last_updated', 'created_at'
        ]
