from rest_framework import serializers
from django.contrib.auth import get_user_model
from .swagModel import fakeModel
User = get_user_model()

class MyTokenObtainPairSerializerSwag(serializers.ModelSerializer):
    
    refresh = serializers.SerializerMethodField()
    access = serializers.SerializerMethodField()
    class Meta:
        model = fakeModel
        fields = ["refresh", "access"]


class BaseUserSerializerSwag(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "email"]

