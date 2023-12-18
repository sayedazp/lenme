from .models import LoanRequest, Account, Offer, ScheduledPayment
from django.shortcuts import get_object_or_404
from rest_framework import exceptions
from django.db.models import Q
from django.db import transaction
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.core.cache import cache
from decimal import Decimal
import heapq
from payment.services import fundPayment, installmentPayment
from django.db.utils import IntegrityError




def createLoanRequest(request, data):
    data.update({"borrowerAccount":request.user.account})
    try:
        loanRequest = LoanRequest.objects.create(
            **data
        )
    except IntegrityError as e:
        raise exceptions.ValidationError({
            "details":e.__cause__
        })
    return loanRequest

def createOffer(request, data, id):
    loanRequest = get_object_or_404(LoanRequest, pk=id)
    lenderAccount = request.user.account
    checkLenderBalance(lenderAccount, loanRequest)
    data.update({"lenderAccount":request.user.account, "loanRequest":loanRequest})
    try:
        offer = Offer.objects.create(
            **data
    )
    except IntegrityError as e:
        raise exceptions.ValidationError({
            "details":e.__cause__
        })
    return offer

def checkLenderBalance(lenderAccount, loanRequest):
    if lenderAccount.balance < loanRequest.totalLoanAmount:
        raise exceptions.NotAcceptable({
            "balance":"Lender account balance can't be less than the loan amount"
        })

@transaction.atomic
def acceptOffer(self, request, serializer, id):
    offer = self.get_object()
    loanRequest = offer.loanRequest
    if loanRequest.borrowerAccount.user != request.user:
        raise exceptions.NotAuthenticated({
            "user", "You are not authorized to perform this action"
        })
    if loanRequest.status == "funded":
        raise exceptions.NotAuthenticated({
            "funded": "The loan is already funded"
        })
    if offer.status == "accepted":
        raise exceptions.ValidationError({
            "status":"offer is already accepted"
        })
    if offer.status == "rejected":
        raise exceptions.ValidationError({
            "status":"can't accept previously rejected offers"
        })
    if offer.status == "rejected":
        raise exceptions.ValidationError({
            "status":"can't accept previously rejected offers"
        })
    checkLenderBalance(offer.lenderAccount, offer.loanRequest)
    loanRequest = offer.loanRequest
    loanRequest.status = "funded"
    offer.status = "accepted"
    offer.save(update_fields=["status"])
    loanRequest.save(update_fields=["status"])
    schedulePayments(offer)
    loanFund(offer.lenderAccount, request.user.account, loanRequest)
    return offer

def getScheduledPayment(offerId):
    offer = get_object_or_404(Offer, pk=offerId)
    return createPaymentPQ(offer)

@transaction.atomic
def schedulePayments(offer):
    numberOfPayments = offer.loanRequest.monthlyPeriod
    priority = 1
    borrowerAccount = offer.loanRequest.borrowerAccount
    lenderAccount = offer.lenderAccount
    while priority <= numberOfPayments:
        dueDate = timezone.now() + relativedelta(months=1*priority)
        payment = ScheduledPayment.objects.create(
            lenderAccount = lenderAccount,
            borrowerAccount = borrowerAccount,
            offer = offer,
            priority = priority,
            dueDate = dueDate
        )
        payment.save()
        priority += 1

def createPaymentPQ(offer:Offer):
    payments = offer.offerSchedPayment.all()
    priorityQueue = []
    for payment in payments:
        if payment.status == "pending":
            priorityQueue.append((payment.priority, payment))
    if len(priorityQueue) == 0:
        raise exceptions.NotFound({
            "payment":"couldn't find payment for the offer"
        })
    heapq.heapify(priorityQueue)
    return heapq.heappop(priorityQueue)[1]

@transaction.atomic
def preparePayInstallment(self):
    installment = self.get_object()
    offer = installment.offer
    scheduledPayment = createPaymentPQ(offer)

    if installment != scheduledPayment:
        raise exceptions.NotAcceptable({
                "payment":"please process pending payments first"
            })
    borrowerAccount = installment.borrowerAccount
    if borrowerAccount.balance < installment.paymenAmount:
        raise exceptions.NotAcceptable({
                "balance":"borrower account balance can't be less than the installment"
            })

    payInstallment(installment.lenderAccount, borrowerAccount, scheduledPayment)
    installment.status = "waiting"
    installment.save(update_fields=["status"])
    return scheduledPayment

@transaction.atomic
def loanFund(lenderAccount:Account, borrowerAccount:Account, loan:LoanRequest):
    laonAmount = loan.totalLoanAmount
    lenderAccount.balance -= laonAmount
    lenderAccount.lockedBalance += laonAmount
    lenderAccount.save(update_fields=["balance", "lockedBalance"])
    fundPayment(laonAmount, lenderAccount, borrowerAccount, loan)

@transaction.atomic
def payInstallment(lenderAccount:Account, borrowerAccount:Account, installment:ScheduledPayment):
    installmentAmount = installment.paymenAmount
    borrowerAccount.balance -= installmentAmount
    borrowerAccount.lockedBalance += installmentAmount
    borrowerAccount.save(update_fields=["balance", "lockedBalance"])
    installmentPayment(installmentAmount, lenderAccount, borrowerAccount, installment)

