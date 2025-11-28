from rest_framework import serializers
from django.utils import timezone
from .models import (
    Subscription,
    SubscriptionPlan,
    SubscriptionHistory,
    PinnedPost
) 

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Сериализатор для тарифных планов"""
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'price', 'duration_days', 'features', 
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        '''Переопределение для гарантии корректного вывода'''
        data = super().to_representation(instance)

        # Убедиться, что feauters - это объект
        if not data.get('features'):
            data['feauters'] = {}

        return data
    
class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки"""
    plan_info = SubscriptionPlanSerializer(source='plan', read_only=True)
    user_info = serializers.SerializerMethodField()
    is_active = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'user_info', 'plan', 'plan_info', 'status',
            'start_date', 'end_date', 'auto_renew', 'is_active',
            'days_remaining', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'start_date', 'end_date',
            'created_at', 'updated_at'
        ]

    def get_user_info(self, obj):
        """Возвращает информацию о пользователе"""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'full_name': obj.user.full_name,
            'email': obj.user.email,
        }