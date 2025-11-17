from django.db.models import (
    CharField,
    TextField,
    IntegerField,
    DateTimeField,
    BooleanField,
    EmailField,
    ImageField
)
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = EmailField(unique=True)
    first_name = CharField(max_length=30, blank=True)
    last_name = CharField(max_length=30, blank=True)
    avatar = ImageField(upload_to='avatars/', blank=True, null=True)
    bio = TextField(max_length=500, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    is_active = BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
