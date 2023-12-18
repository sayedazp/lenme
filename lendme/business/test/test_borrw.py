from django.test import TestCase
from business.models import LoanRequest
from payment.models import ScheduledPayment
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse_lazy
from payment.fakePaymentGetway import PaymentGetway
User = get_user_model()
from rest_framework import status
class BorrowingFunctionalityTestCase(TestCase):

    def setUp(self):
        """creating borrower and lender accounts"""
        ##borrower account
        borrowerSignupurl = reverse_lazy("borrowersignup")
        lenderSignupurl = reverse_lazy("lendersignup")
        self.borrowerClient = APIClient()
        self.lenderClient = APIClient()
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

        ### lender account
        self.lenderClient.post(lenderSignupurl, ({"username":"root",
                                                        "email":"root@root.com",
                                                        "password":"root"}), format='json')
        self.createdLenderUser = User.objects.get(username="root")
        self.createdLenderUser.account.balance = 500000
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
        submitloanrequestUrl = reverse_lazy("submitloanrequest")
        
        createLoanResponse = self.borrowerClient.post(submitloanrequestUrl, data=
            {
                "principle":"6000",
                "monthlyPeriod":6
            },
            format='json',
        )
        self.loanRequest_id = createLoanResponse.json()['id']

        ##creating an offer to begin with
        offerCreateResponse = self.lenderClient.post(reverse_lazy("offercreate", args=[self.loanRequest_id]), data=
            {
                 "interestRate":".25"
            },
            format='json',
        )

    def test_PaymentFunctionality(self):
        """test payment system and celery functions repayment schedules and loan funding"""

        ## borrower user viewing all offers
        allOffers = self.borrowerClient.get(reverse_lazy("alloffer"))

        self.assertEqual(allOffers.status_code, status.HTTP_200_OK)

        allLoanRequests = self.lenderClient.get(reverse_lazy("allloanrequests"))

        self.assertEqual(allLoanRequests.status_code, status.HTTP_200_OK)

        acceptOffer = self.borrowerClient.patch(reverse_lazy("offeraccept", args=[allOffers.json()[0]['id']]))  
        
        self.assertEqual(acceptOffer.status_code, status.HTTP_200_OK)  
        
        scheduledPayment = self.borrowerClient.get(reverse_lazy("offerschedpayment", args=[allOffers.json()[0]['id']]))
        
        self.assertEqual(scheduledPayment.status_code, status.HTTP_200_OK)
        
        payschedpayment = self.borrowerClient.patch(reverse_lazy("payschedpayment", args=[scheduledPayment.json()['id']]))
        
        self.assertEqual(payschedpayment.status_code, status.HTTP_200_OK)
        
        installmentPayment = ScheduledPayment.objects.get(id=scheduledPayment.json()["id"]).paymentInstallment.get()
        
        
        
        ## the fake payment getway has a 20% to refuse a payment
        loanRequest = LoanRequest.objects.get(id=self.loanRequest_id)
        loanRequestPayment = loanRequest.paymentRequest.get()

        self.assertEqual(loanRequestPayment.persisted, False)
        self.assertEqual(loanRequestPayment.status, 'pending')
        self.assertEqual(installmentPayment.persisted, False)
        self.assertEqual(installmentPayment.status, 'pending')
        

        
        self.celreyPaymentGetwayWorkerSimulator(installmentPayment.id, "installment")
        self.celreyPaymentGetwayWorkerSimulator(loanRequestPayment.id, "loanFund")
        self.celeryBeatSimulator()
        loanRequestPayment.refresh_from_db()
        loanRequest.refresh_from_db()
        installmentPayment.refresh_from_db()


        self.assertEqual(loanRequestPayment.persisted, True)
        self.assertIn(loanRequestPayment.status, ['accepted', 'rejected'])
        self.assertEqual(installmentPayment.persisted, True)
        self.assertIn(installmentPayment.status, ['accepted', 'rejected'])
        self.assertEqual(self.createdborrowerUser.account.type, "borrower")
        self.assertEqual(self.createdLenderUser.account.type, "lender")

    def celreyPaymentGetwayWorkerSimulator(self, paymentId, type):
        """celery payment getway simulator"""
        PaymentGetway.pay(paymentId, type)
    def celeryBeatSimulator(self):
        """simulate celery beat behaviour to manage payments"""
        from payment.services import installmentPaymentCleaner, loanPaymentCleaner
        installmentPaymentCleaner()
        loanPaymentCleaner()
    
