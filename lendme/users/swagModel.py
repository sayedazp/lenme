from django.db import models

class fakeModel(models.Model):
     class meta:
          abstract = True