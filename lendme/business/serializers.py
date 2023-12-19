from rest_framework import serializers
from .models import LoanRequest, Account, Offer, ScheduledPayment

class AccountSerializer(serializers.ModelSerializer):   
    username = serializers.SerializerMethodField()
    class Meta:
        model = Account
        read_only_fields = ["balance"]
        fields=["username"]
    
    def get_username(self, instance):
        return instance.username

class LoadnRequestSerializer(serializers.ModelSerializer):
    borrowerAccount = AccountSerializer(read_only = True)
    class Meta:
        model = LoanRequest
        read_only_fields = ['businessFee', 'status', 'created_at']
        fields = "__all__"

class OfferSerializer(serializers.ModelSerializer):
    lenderAccount = AccountSerializer(read_only = True)
    loanRequest = LoadnRequestSerializer(read_only = True)

    class Meta:
        model = Offer
        read_only_fields = ['created_at', 'status']
        fields = ['id', 'interestRate', 'status', 'lenderAccount', 'loanRequest']

class patchOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ['status']
        read_only_fields = ['status']

class ScheduledPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledPayment
        fields = "__all__"

class PatchScheduledPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledPayment
        read_only_fields = ['status', 'dueDate']
        fields = ['status', 'dueDate']
