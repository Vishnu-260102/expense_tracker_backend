# Generated by Django 4.1.7 on 2023-09-28 11:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MonthlySalary',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('month', models.CharField(max_length=20)),
                ('year', models.CharField(max_length=5)),
                ('salary', models.CharField(max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'monthly_salary',
            },
        ),
        migrations.CreateModel(
            name='ExpenseDetails',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('month', models.CharField(max_length=20)),
                ('year', models.CharField(max_length=5)),
                ('expense_name', models.CharField(max_length=100)),
                ('expense_description', models.TextField()),
                ('expense_date', models.DateField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'expense_details',
            },
        ),
    ]