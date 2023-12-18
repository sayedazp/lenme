from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, serializers
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer, BaseUserSerializer
from rest_framework import generics, mixins
from .services import createAccount

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class SignUp(mixins.CreateModelMixin,
                    generics.GenericAPIView):

    serializer_class =  BaseUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        createAccount(request=request, data = serializer.validated_data, type=self.type)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class BorrowerSignUp(SignUp):
    type = "borrower"
class LenderSignUp(SignUp):
    type = "lender"
