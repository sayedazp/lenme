from celery import shared_task
from .services import helper

@shared_task
def paymentCheck():
    helper()
