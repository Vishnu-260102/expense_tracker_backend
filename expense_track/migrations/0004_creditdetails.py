# Generated by Django 4.1.7 on 2023-10-04 08:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('expense_track', '0003_expensedetails_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditDetails',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('month', models.CharField(max_length=20)),
                ('year', models.CharField(max_length=5)),
                ('credit_name', models.CharField(max_length=100)),
                ('credit_description', models.TextField()),
                ('credit_date', models.DateField()),
                ('amount', models.CharField(max_length=100)),
                ('monthly_salary', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='expense_track.monthlysalary')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'credit_details',
            },
        ),
    ]
