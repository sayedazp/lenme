from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse_lazy
from rest_framework import status
User = get_user_model()

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
        
        self.createLoanResponse = self.borrowerClient.post(submitloanrequestUrl, data=
            {
                "principle":"6000",
                "monthlyPeriod":6
            },
            format='json',
        )
        self.loanRequest_id = self.createLoanResponse.json()['id']

    def test_canFund(self):
        """valid lender funding"""
        can_fund = self.lenderClient.get(reverse_lazy("checkoffercreate", args=[self.loanRequest_id,]))
        self.assertEqual(can_fund.status_code, status.HTTP_200_OK)

    def test_cantFund(self):
        """not valid lender funding"""
        ledneracc = self.createdLenderUser.account
        ledneracc.balance = 0
        ledneracc.save()
        can_fund = self.lenderClient.get(reverse_lazy("checkoffercreate", args=[self.loanRequest_id,]))
        self.assertEqual(can_fund.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_noOrWrongAuthorized(self):
        """not authorized lender fund"""
        can_fundWrongAuth = self.borrowerClient.get(reverse_lazy("checkoffercreate", args=[self.loanRequest_id,]))
        client = APIClient()
        can_fundNoAuth = client.get(reverse_lazy("checkoffercreate", args=[self.loanRequest_id,]))
        self.assertEqual(can_fundWrongAuth.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(can_fundNoAuth.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_wrongLoanId(self):
        """funding wrong loan"""
        can_fundWrongId = self.lenderClient.get(reverse_lazy("checkoffercreate", args=[100,]))
        self.assertEqual(can_fundWrongId.status_code, status.HTTP_404_NOT_FOUND)
