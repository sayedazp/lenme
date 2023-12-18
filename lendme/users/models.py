from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True, null=False, blank=False, error_messages={
        "unique":"A user with the same email already exists"
    })
    account = models.OneToOneField("business.Account", on_delete=models.CASCADE, null=False, blank=False, related_name="user")
