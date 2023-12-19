"""A custom module for swagger documentation purposes only"""
from rest_framework import serializers
from .models import LoanRequest, Offer


class LoadnRequestSerializerswag(serializers.ModelSerializer):
    class Meta:
        model = LoanRequest
        read_only_fields = ['businessFee', 'status', 'created_at']
        exclude=["borrowerAccount"]

class OfferSerializerSwag(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ['status']
