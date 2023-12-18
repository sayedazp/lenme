from django.test import TestCase, TransactionTestCase
from business.models import LoanRequest, Account, Offer
from payment.models import ScheduledPayment, InstallmentPayment
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status
from users.views import BorrowerSignUp
from django.urls import reverse_lazy
from payment.fakePaymentGetway import PaymentGetway
from django.db import transaction
User = get_user_model()

class lenderOfferFunctionalityTestCase(TransactionTestCase):

    def setUp(self):
        """creating borrower and lender accounts"""
        ##borrower account
        borrowerSignupurl = reverse_lazy("borrowersignup")
        lenderSignupurl = reverse_lazy("lendersignup")
        self.borrowerClient = APIClient()
        self.lenderClient = APIClient()
        self.nonAuthClient = APIClient()
        authUrl = reverse_lazy("token_obtain_pair")
        self.borrowerClient.post(borrowerSignupurl, ({"username":"roet",
                                                        "email":"roet@root.com",
                                                        "password":"roet"}), format='json')
        self.createdborrowerUser = User.objects.get(username="roet")
        self.createdborrowerUser.account.balance = 50000
        authResponse = self.borrowerClient.post(authUrl, data=
            {
                "username":"roet",
                "password":"roet"
            },
            format='json'
        )
        borrowertoken = authResponse.json()['access']
        self.borrowerClient.credentials(HTTP_AUTHORIZATION='Bearer ' + borrowertoken)

        self.lenderClient.post(lenderSignupurl, ({"username":"root",
                                                        "email":"root@root.com",
                                                        "password":"root"}), format='json')
        self.createdLenderUser = User.objects.get(username="root")
        self.createdLenderUser.account.balance = 500000
        self.createdborrowerUser.account.balance = 50000
        authLenderResponse = self.lenderClient.post(authUrl, data=
            {
                "username":"root",
                "password":"root"
            },
            format='json'
        )

        lenderToken= authLenderResponse.json()['access']
        self.lenderClient.credentials(HTTP_AUTHORIZATION='Bearer ' + lenderToken)
        self.createdLenderUser.save()
        self.createdLenderUser.account.save()
        self.createdborrowerUser.save()
        self.createdborrowerUser.account.save()

        loanRequestResponse = self.borrowerClient.post(reverse_lazy("submitloanrequest"), data={
            "principle":6000,
            "monthlyPeriod":6
        })
        self.offer = LoanRequest.objects.get(id=loanRequestResponse.json()["id"])

    def test_offerCreateAPI(self):
        validRequest1 = self.lenderClient.post(reverse_lazy("offercreate", args=[self.offer.id]), data={
            "interestRate":.25,
        })
        validRequest2 = self.lenderClient.post(reverse_lazy("offercreate", args=[self.offer.id]), data={
        })
        notValidRequest1 = self.lenderClient.post(reverse_lazy("offercreate", args=[self.offer.id]), data={
            "interestRate":-1,
        })
        notValidRequest2 = self.lenderClient.post(reverse_lazy("offercreate", args=[self.offer.id]), data={
            "interestRate":0,
        })

        self.assertEqual(validRequest1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(validRequest2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(notValidRequest1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(notValidRequest2.status_code, status.HTTP_400_BAD_REQUEST)
