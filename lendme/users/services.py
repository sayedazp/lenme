from business.models import Account
from .models import User
from django.db import transaction

@transaction.atomic
def createAccount(*,data, request, type):
    acc = Account.objects.create(type=type)
    user = User.objects.create_user(account = acc, email=data["email"],password = data["password"], username=data["username"])
    user.save()
    return user
