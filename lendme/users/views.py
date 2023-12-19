from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, serializers
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer, BaseUserSerializer
from rest_framework import generics, mixins
from .services import createAccount
from . import swagerSerializer
from drf_yasg.utils import swagger_auto_schema

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    
    @swagger_auto_schema(
                operation_id="jwt token obtain(login)",
                operation_description="authenticate and login user using its username and password",
                operation_summary="any",
                responses={
                    201:swagerSerializer.MyTokenObtainPairSerializerSwag
                }
            )
    def post(self, request: Request, *args, **kwargs) -> Response:
        return super().post(request, *args, **kwargs)

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

    @swagger_auto_schema(
                operation_id="Create new borrower user",
                operation_description="Create new borrower user endpoint creates a user and configures its default balance",
                operation_summary="any",
                responses={
                    201:swagerSerializer.BaseUserSerializerSwag
                }
            )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
class LenderSignUp(SignUp):
    type = "lender"

    @swagger_auto_schema(
                operation_id="Create new lender user",
                operation_description="Create new lender user endpoint creates a user and configures its default balance",
                operation_summary="any",
                responses={
                    201:swagerSerializer.BaseUserSerializerSwag
                }
            )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
