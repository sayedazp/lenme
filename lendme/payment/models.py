from django.db import models
from business.models import LoanRequest, Account, ScheduledPayment

class Payment(models.Model):
    STATUS = [
        ("1", "accepted"), ## successfully paid payment
        ("2", "rejected"), ## rejected payment
        ("3", "pending"), ## waiting to be handled and default
    ]
    amount = models.DecimalField(blank=False, null=False, default=0.0, decimal_places=2, max_digits=15)
    status = models.CharField(choices=STATUS, max_length=2, null=False, default="pending")
    persisted = models.BooleanField(null = False, default=False, blank=False)
    date_issued = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class InstallmentPayment(Payment):
    sender = models.ForeignKey(Account, null=False, blank=False, on_delete=models.CASCADE, related_name="installment_payment_Sender")
    reciever = models.ForeignKey(Account, null=False, blank=False, on_delete=models.CASCADE, related_name="installment_payment_Reciever")
    scheduledPayment = models.ForeignKey(ScheduledPayment, null=False, blank=False, on_delete=models.CASCADE, related_name="paymentInstallment")

class LoanPayment(Payment):
    sender = models.ForeignKey(Account, null=False, blank=False, on_delete=models.CASCADE, related_name="loan_payment_Sender")
    reciever = models.ForeignKey(Account, null=False, blank=False, on_delete=models.CASCADE, related_name="loan_payment_Reciever")
    loanRequest = models.ForeignKey(LoanRequest, null=False, blank=False, on_delete=models.CASCADE, related_name="paymentRequest")
