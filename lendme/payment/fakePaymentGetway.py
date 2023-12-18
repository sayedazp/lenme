import random
from .models import Payment, InstallmentPayment, LoanPayment

class PaymentGetway:
    outputs = [True, False]

    @classmethod
    def pay(self, paymentId, type) -> bool:
        if type == "installment":
            paymentClass = InstallmentPayment
        else:
            paymentClass = LoanPayment
        payment = paymentClass.objects.get(pk=paymentId)
        success = random.choices(population=self.outputs, weights=(80, 20), k=1)
        if success:
            payment.status = "accepted"
            payment.save(update_fields=["status"])
        else:
            payment.status = "rejected"
            payment.save(update_fields=["status"])
