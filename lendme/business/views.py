from django.shortcuts import render
from rest_framework import generics, mixins, permissions
from .models import LoanRequest, Offer, ScheduledPayment
from .serializers import LoadnRequestSerializer, OfferSerializer, patchOfferSerializer, ScheduledPaymentSerializer
from .permissions import BorrowerPermission, LenderPermission
from .services import createLoanRequest, createOffer, acceptOffer, getScheduledPayment, preparePayInstallment, checkLenderBalance
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.cache import cache

class LoanRequestListApiView(mixins.ListModelMixin,
                  generics.GenericAPIView):
    serializer_class = LoadnRequestSerializer
    permission_classes = [permissions.IsAuthenticated, LenderPermission]

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
    serializer_class = LoadnRequestSerializer

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

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        criterion = Q(loanRequest__borrowerAccount__user=self.request.user)
        return Offer.objects.filter(criterion)

class OfferAcceptApiView(mixins.UpdateModelMixin,
                         generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, BorrowerPermission]
    serializer_class = patchOfferSerializer

    def get_queryset(self):
        pass

    def patch(self, request, *args, **kwargs):
        self.partial_update(request, *args, **kwargs)
        cache.delete("loanRequests")
        return Response({
            "status":"accepted"
        })
    def perform_update(self, serializer):
        return acceptOffer(self=self, serializer=serializer, request=self.request, id=self.kwargs["pk"])
    
    def get_object(self):
        return get_object_or_404(Offer, id=self.kwargs["pk"])

class ScheduledPaymentRetrieveAPIView(mixins.RetrieveModelMixin,
                      generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, BorrowerPermission]
    serializer_class = ScheduledPaymentSerializer


    def get_queryset(self):
        pass

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_object(self):
        payment = getScheduledPayment(self.kwargs["pk"])
        return payment
    

class payInstallmentApiView(mixins.UpdateModelMixin,
                         generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, BorrowerPermission]
    serializer_class = ScheduledPaymentSerializer
    
    def get_queryset(self):
        pass


    def patch(self, request, *args, **kwargs):
        self.partial_update(request, *args, **kwargs)
        return Response({
            "status":"payment is being processed"
        })
    def perform_update(self, serializer):
        return preparePayInstallment(self)

    def get_object(self):
        return get_object_or_404(ScheduledPayment, id=self.kwargs["pk"])

