# Generated by Django 5.1.7 on 2025-04-08 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gmocs', '0002_remove_registrations_payment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrations',
            name='members',
            field=models.JSONField(default=list),
        ),
    ]
