from rest_framework import serializers, status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from business.models import Account
from business.serializers import AccountSerializer
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        # ...
        return token

class BaseUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "password", "email"]
        extra_kwargs = {
            "password":{"write_only": True},
        }
