# Generated by Django 4.1.7 on 2023-09-29 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expense_track', '0002_expensedetails_monthly_salary'),
    ]

    operations = [
        migrations.AddField(
            model_name='expensedetails',
            name='amount',
            field=models.CharField(default='200', max_length=100),
            preserve_default=False,
        ),
    ]
