# Generated by Django 5.0 on 2023-12-17 17:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0011_account_lockedbalance_alter_scheduledpayment_duedate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduledpayment',
            name='dueDate',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 17, 17, 22, 24, 818380, tzinfo=datetime.timezone.utc)),
        ),
    ]
