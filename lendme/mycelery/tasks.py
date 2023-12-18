from celery import shared_task
from payment.fakePaymentGetway import PaymentGetway

@shared_task(bind=True)
def pay(self, paymentId, type):
    PaymentGetway.pay(paymentId, type)

