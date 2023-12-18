from .models import LoanPayment, InstallmentPayment, Account, LoanRequest, ScheduledPayment
from mycelery.tasks import pay
from django.db import transaction
from django.db.models import Q

def fundPayment(amount, sender, reciever, loanRequest):
    payment = LoanPayment.objects.create(
        sender=sender,
        reciever=reciever,
        amount=amount,
        loanRequest = loanRequest
    )
    pay.delay(payment.id, "loan")

def installmentPayment(amount, sender, reciever, scheduledPayment):
    payment = InstallmentPayment.objects.create(
        sender=sender,
        reciever=reciever,
        amount=amount,
        scheduledPayment = scheduledPayment
    )
    pay.delay(payment.id, "installment")

def installmentPaymentCleaner():
    criterion:Q = ~Q(status="pending") & Q(persisted=False)
    unhandledPayments = InstallmentPayment.objects.filter(criterion)
    for payment in unhandledPayments:
        if payment.status == "accepted":
            installmentPaymentSuccess(payment)
        else:
            installmentPaymenrFail(payment)

@transaction.atomic
def installmentPaymentSuccess(payment:InstallmentPayment):
    scheduledPayment:ScheduledPayment = payment.scheduledPayment
    lender:Account = payment.reciever
    borrower:Account = payment.sender
    borrower.lockedBalance -= payment.amount
    lender.balance += payment.amount
    scheduledPayment.status = "paid"
    payment.persisted = True
    payment.save(update_fields=["persisted"])
    borrower.save()
    lender.save()
    scheduledPayment.save(update_fields=["status"])

@transaction.atomic
def installmentPaymenrFail(payment:InstallmentPayment):
    scheduledPayment:ScheduledPayment = payment.scheduledPayment
    borrower:Account = payment.sender
    borrower.lockedBalance -= payment.amount
    borrower.balance += payment.amount
    scheduledPayment.status = "pending"
    payment.persisted = True
    payment.save(update_fields=["persisted"])
    borrower.save()
    scheduledPayment.save(update_fields=["status"])



def loanPaymentCleaner():
    criterion:Q = ~Q(status="pending") & Q(persisted=False)
    unhandledPayments = LoanPayment.objects.filter(criterion)
    for payment in unhandledPayments:
        if payment.status == "accepted":
            fundPaymentSuccess(payment)
        else:
            fundPaymentFail(payment)

@transaction.atomic
def fundPaymentSuccess(payment:LoanPayment):
    loan:LoanRequest = payment.loanRequest
    lender:Account = payment.reciever
    borrower:Account = payment.sender
    lender.lockedBalance -= payment.amount
    borrower.balance += payment.amount
    loan.status = "funded"
    payment.persisted = True
    payment.save(update_fields=["persisted"])
    loan.save(update_fields=["status"])
    borrower.save()
    lender.save()

@transaction.atomic
def fundPaymentFail(payment:LoanPayment):
    lender:Account = payment.sender
    lender.lockedBalance -= payment.amount
    lender.balance += payment.amount
    payment.persisted = True
    payment.save(update_fields=["persisted"])
    lender.save()
