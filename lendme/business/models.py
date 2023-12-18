from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils import timezone
from decimal import Decimal
from django.utils import timezone

class Account(models.Model):

    ACCOUNTTYPES = [
    ("1","borrower"),
    ("2", "lender")
    ]
    
    balance = models.DecimalField(blank=False, null=False, default=0.0, decimal_places=2, max_digits=15)
    lockedBalance = models.DecimalField(blank=False, null=False, default=0.0, decimal_places=2, max_digits=15)
    type = models.CharField(blank=False, null=False, choices=ACCOUNTTYPES, max_length=2)

    @property
    def username(self):
        return self.user.username

class LoanRequest(models.Model):
    STATUS = [
        ("1", "pending"),
        ("2", "funded"),
    ]
    borrowerAccount = models.ForeignKey(Account, on_delete = models.CASCADE, related_name="account_loan_requests")
    principle = models.DecimalField(blank=False, null=False, decimal_places=2, max_digits = 15, default=6000)
    monthlyPeriod = models.PositiveIntegerField(blank=False, null=False, default=6)
    businessFee = models.DecimalField(blank=False, null=False, decimal_places=2, max_digits = 15, default=3.75)
    status = models.CharField(choices=STATUS, max_length=2, default="pending")
    created_at = models.DateTimeField(auto_now=True)

    @property
    def totalLoanAmount(self):
        return self.principle + self.businessFee

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(principle__gt=0),
                name="check positive principle values"
            ),
            CheckConstraint(
                check=Q(monthlyPeriod__gt=0),
                name="check positive monthlyPeriod values"
            ),
            CheckConstraint(
                check=Q(businessFee__gte=0),
                name="check positive or zero fee values"
            )
        ]

class Offer(models.Model):
    roundingPlaces = Decimal('0.001') #3places

    STATUS = [
        ("1", "pending"),
        ("2", "accepted"),
        ("3", "rejected")
    ]
    lenderAccount = models.ForeignKey(Account, on_delete = models.CASCADE, related_name="lender_account_offers")
    loanRequest = models.ForeignKey(LoanRequest, on_delete=models.CASCADE, related_name="loan_request_offers")
    interestRate = models.DecimalField(decimal_places=4, max_digits=10, null=False, blank=False, default = 0.15)
    status = models.CharField(choices=STATUS, max_length=2, null=False, default="pending")
    created_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(interestRate__gt=0),
                name="check positive interest rate values"
            ),
        ]

    @property
    def totalCost(self):
        interest = ((Decimal(self.interestRate)*Decimal(self.loanRequest.principle)*Decimal(Decimal(self.loanRequest.monthlyPeriod)/12)) + Decimal(self.loanRequest.businessFee)).quantize(Decimal('0.001'))
        interest = interest.quantize(self.roundingPlaces)
        return (interest + Decimal(self.loanRequest.totalLoanAmount))

    ##lenme policy doesn't charge borrowers any fees, but it seems that the task state otherwise
    @property
    def installment(self):
        ins = (self.totalCost/Decimal(self.loanRequest.monthlyPeriod)).quantize(self.roundingPlaces)
        return ins

class ScheduledPayment(models.Model):
    STATUS = [
        ("1", "paid"), ## successfully paid payment
        ("2", "pending"), ## default value for queued as a scheduled
        ("4", "waiting") ## waiting for the payment getway to confirm the payment
    ]

    lenderAccount = models.ForeignKey(Account, on_delete = models.CASCADE, related_name="lender_account_sched_payments")
    borrowerAccount = models.ForeignKey(Account, on_delete = models.CASCADE, related_name="borrower_account_sched_payments")
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="offerSchedPayment")
    status = models.CharField(choices=STATUS, max_length=2, null=False, default="pending")
    dueDate = models.DateTimeField(null = False, default = timezone.now())
    priority = models.PositiveIntegerField(blank=False, null=False)

    @property
    def isLastPayment(self):
        return self.priority == self.offer.loanRequest.monthlyPeriod
    @property
    def paymenAmount(self):
        return self.offer.installment
