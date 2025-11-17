from django.forms import ValidationError
from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    ValidationError,
    Serializer,
    EmailField,
    ReadOnlyField,
    SerializerMethodField
)
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password


from .models import User


class UserRegistrationSerializer(ModelSerializer):
    password = CharField(
        write_only = True,
        validators = [validate_password]
    )
    
    password_confirm  = CharField(
        write_only = True
    )
    
    class Meta:
        model = User
        fields = (
            'username','email','password','password_confirm'
        )
    
    
    def validate(self,attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise ValidationError(
                {"password":"is a not correct"}
            )
        return attrs


    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user
    
    
class UserLoginSerializer(Serializer):
    email = EmailField()
    password = CharField(write_only=True)
    
    
    def validate(self,attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username = email,
                password = password
            )
            if not user:
                raise ValidationError(
                    'User not found'
                )
            if not user.is_active:
                raise ValidationError(
                    'User account is disabled'
                )
            attrs['user'] = user
            return attrs
        else:
            raise ValidationError(
                'Must include "email" and "password".'
            )
            

class UserProfileSerializer(ModelSerializer):
    full_name = ReadOnlyField()
    posts_count = SerializerMethodField()
    comments_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'avatar', 'bio', 'created_at', 'updated_at',
            'posts_count', 'comments_count'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    
    def get_posts_count(self,obj):
        try:
            return obj.posts.count()
        except AttributeError:
            return 0
    
    def get_comments_count(self,obj):
        try:
            return obj.comments.count()
        except AttributeError:
            return 0
        
class UserUpdateSerializer(ModelSerializer):
    
    class Meta:
        model = User
        fields = (
            'first_name','last_name','bio','avatar'
        )
    
    def update(self,instance,validated_data):
        for attrs,value in validated_data.items():
            setattr(instance,attrs,value)
        instance.save()
        return instance
    
    
class UserChangePasswordSerializer(Serializer):
    old_password = CharField(required = True)
    new_password = CharField(
        write_only = True,
        validators = [validate_password]
    )
    new_password_confirm = CharField(required=True)
    
    
    def validate_old_password(self,value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError(
                'Old password is not correct'
            )
        return value
    
    
    def validate(self,attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise ValidationError(
                'Is a password is not correct '
            )
    
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user