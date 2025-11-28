from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class SubscriptionPlan(models.Model):
    """Модель тарифного плана подписки"""
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField(default=30)
    stripe_price_id = models.CharField(max_length=255, unique=True)
    features = models.JSONField(default=dict, help_text="Список возможностей подписки")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscription_plans'
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
        ordering = ['price']

    def __str__(self):
        return f"{self.name} - ${self.price}"
    
    
class Subscription(models.Model):
    """Модель подписки пользователя"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscriptions'
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['end_date', 'status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"
    
    @property
    def is_active(self):
        return (
            self.status == "active" and
            self.end_date > timezone.now()
        )
        
    @property
    def days_remaning(self):
        if not self.is_active:
            return 0

        delta = self.end_date - timezone.now()
        
        return max(0,delta.days)    

    
    def extend_subscribe(self,days=30):
        if self.is_active:
            self.end_date +=timedelta(days=days)
        else:
            self.start_date =timezone.now()
            self.end_date = self.start_date + timedelta(days)
            self.status = 'active'
        self.save()
    
    
    def canceled(self):
        self.status = 'cancelled'
        self.auto_renew = False
        self.save()
        
        
    def expire(self):
        self.status = 'expired'
        self.save()
        
        
    def active(self):
        self.status = 'active'
        self.start_date = timezone.now()
        self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        self.save()
        

class PinnedPost(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pinned_post'
    )
    
    post = models.ForeignKey(
        'main.Post',
        on_delete=models.CASCADE,
        related_name='pin_info'
    )
    
    pinned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'pinned_posts'
        verbose_name = 'Pinned Post'
        verbose_name_plural = 'Pinned Posts'
        ordering = ['pinned_at']
        indexes = [
            models.Index(fields=['pinned_at']),
        ]

    def __str__(self):
        return f"{self.user.username} pinned: {self.post.title}"
    
    
    def save(self,*args,**kwargs):
        if not hasattr(self.user,'subscription') or not self.user.subscription.is_active:
            raise ValueError('User must have an active subscription to pin posts.')
        
        if self.post.author != self.user:
            raise ValueError('User can only pin their own posts.')
        
        super().save(*args, **kwargs)
        

class SubscriptionHistory(models.Model):
    """История изменений подписки"""
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('activated', 'Activated'),
        ('renewed', 'Renewed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('payment_failed', 'Payment Failed'),
    ]

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='history'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subscription_history'
        verbose_name = 'Subscription History'
        verbose_name_plural = 'Subscription History'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subscription.user.username} - {self.action}"
        
    