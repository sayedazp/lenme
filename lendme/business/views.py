from django.shortcuts import render
from rest_framework import generics, mixins, permissions
from .models import LoanRequest, Offer, ScheduledPayment
from .serializers import LoanRequestSerializer, OfferSerializer, patchOfferSerializer, ScheduledPaymentSerializer, PatchScheduledPaymentSerializer
from .permissions import BorrowerPermission, LenderPermission
from .services import createLoanRequest, createOffer, acceptOffer, getScheduledPayment, preparePayInstallment, checkLenderBalance
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from . import swaggerSerializers

class LoanRequestListApiView(mixins.ListModelMixin,
                  generics.GenericAPIView):
    serializer_class = LoanRequestSerializer
    permission_classes = [permissions.IsAuthenticated, LenderPermission]
    @swagger_auto_schema(
                operation_id="get all requested loans",
                operation_summary="[permissions.IsAuthenticated, LenderPermission]",
                operation_description="This is where the lender navigate through all requested loans on the system",
            )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        loanRequests = cache.get("loanRequests")
        if loanRequests:
            print("cache hit")
            return loanRequests
        else:
            loanRequests = LoanRequest.objects.filter(status="pending")
            cache.set("loanRequests", loanRequests)
        return LoanRequest.objects.filter(status="pending")


class SubmitLoanRequest(mixins.CreateModelMixin,
                        generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, BorrowerPermission]
    serializer_class = LoanRequestSerializer

    @swagger_auto_schema(
            request_body=swaggerSerializers.LoadnRequestSerializerswag,
            operation_summary="[permissions.IsAuthenticated, BorrowerPermission]",
            operation_id="submit a new loan request",
            operation_description="submitting a new loan request",
            responses={
                201:LoanRequestSerializer
            }
        )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        loan = createLoanRequest(request=request, data=serializer.validated_data)
        cache.delete("loanRequests")
        headers = self.get_success_headers(serializer.data)
        return Response(self.get_serializer_class()().to_representation(loan), status=status.HTTP_201_CREATED, headers=headers)

class SubmitOffer(mixins.CreateModelMixin,
                        generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, LenderPermission]
    serializer_class = OfferSerializer

    @swagger_auto_schema(
            request_body=swaggerSerializers.LoadnRequestSerializerswag,
            operation_id="submit a new offer for a specific loan",
            operation_summary="[permissions.IsAuthenticated, LenderPermission]",
            operation_description="submitting a new offer for loan request where loan id is id!",
            responses={
                201:swaggerSerializers.OfferSerializerSwag
            }
        )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        offer = createOffer(request=request, data=serializer.validated_data, id=self.kwargs["id"])
        headers = self.get_success_headers(serializer.data)
        return Response(self.get_serializer_class()().to_representation(offer), status=status.HTTP_201_CREATED, headers=headers)
    def perform_create(self, serializer):
        return super().perform_create(serializer)



class checkCanFundApiView(APIView):
    permission_classes = [permissions.IsAuthenticated, LenderPermission]
    serializer_class = OfferSerializer
    @swagger_auto_schema(
            operation_id="check lender ability fund ability",
            operation_description="checking lender ability to fund a loan based on lender balance and loan request cost",
            operation_summary="[permissions.IsAuthenticated, LenderPermission]"
        )
    def get(self, request, *args, **kwargs):
        loan = self.get_object(request, *args, **kwargs)
        checkLenderBalance(request.user.account, loan)
        return Response({
            "status":"The user can fund that loan"
        }, status=status.HTTP_200_OK)
    def get_object(self, *args, **kwargs):
        return get_object_or_404(LoanRequest, id=kwargs["id"])

class OffersListApiView(mixins.ListModelMixin,
                  generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated, BorrowerPermission]
    serializer_class = OfferSerializer
    @swagger_auto_schema(
                operation_id="get a list of all borrower offer",
                operation_description="borrower user can view all offers presented to him on his different loan requests",
                operation_summary="[permissions.IsAuthenticated, BorrowerPermission]"
            )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        criterion = Q(loanRequest__borrowerAccount__user=self.request.user)
        return Offer.objects.filter(criterion)

class ScheduledPaymentRetrieveAPIView(mixins.RetrieveModelMixin,
                      generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, BorrowerPermission]
    serializer_class = ScheduledPaymentSerializer


    def get_queryset(self):
        pass

    @swagger_auto_schema(
                operation_id="get the scheduled payment that needs to be paid",
                operation_description="This Api uses special functionality to ensure that no payment is paid before the previously scheduled one, so once a payment is successfully paid, a call to this endpoint will bring the next scheduled one if there is any",
                operation_summary="[permissions.IsAuthenticated, BorrowerPermission]"
            )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_object(self):
        payment = getScheduledPayment(self.kwargs["pk"])
        return payment
    

class OfferAcceptApiView(mixins.UpdateModelMixin,
                         generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, BorrowerPermission]
    serializer_class = patchOfferSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Offer.objects.filter(id=self.kwargs["id"])

    @swagger_auto_schema(
                operation_id="accept an offer using its id",
                operation_description="the borrower can accept specific offer using its id, the endpoint ensures that the lender is able to fund in the moment of accepting",
                operation_summary="[permissions.IsAuthenticated, BorrowerPermission]"
            )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    def perform_update(self, serializer):
        acceptOffer(self=self, serializer=serializer, request=self.request, id=self.kwargs["id"])
        cache.delete("loanRequests")


class payInstallmentApiView(mixins.UpdateModelMixin,
                         generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, BorrowerPermission]
    serializer_class = PatchScheduledPaymentSerializer
    lookup_field = "id"

    def get_queryset(self):
        return ScheduledPayment.objects.filter(id=self.kwargs["id"])
    
    @swagger_auto_schema(
                operation_id="Pay specific payment using payment id",
                operation_description="Borrower can pay their payments using this endpoints once they provide the payment id",
                operation_summary="[permissions.IsAuthenticated, BorrowerPermission]"
            )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        return preparePayInstallment(self)
