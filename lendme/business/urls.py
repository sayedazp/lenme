from django.urls import path
from . import views

urlpatterns = [
    path("loan_request/all", views.LoanRequestListApiView.as_view(), name="allloanrequests"),
    path("loan_request/submit", views.SubmitLoanRequest.as_view(), name="submitloanrequest"),
    path("offer/all", views.OffersListApiView.as_view(), name="alloffer"),
    path("offer/check/<int:id>", views.checkCanFundApiView.as_view(), name="checkoffercreate"),
    path("offer/create/<int:id>", views.SubmitOffer.as_view(), name="offercreate"),
    path("offer/accept/<int:id>", views.OfferAcceptApiView.as_view(), name="offeraccept"),
    path("offer/schedpayment/<int:pk>", views.ScheduledPaymentRetrieveAPIView.as_view(), name="offerschedpayment"),
    path("payment/pay/<int:id>", views.payInstallmentApiView.as_view(), name="payschedpayment"),
]
