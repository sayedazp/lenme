def helper():
    from payment.services import installmentPaymentCleaner, loanPaymentCleaner
    installmentPaymentCleaner()
    loanPaymentCleaner()
