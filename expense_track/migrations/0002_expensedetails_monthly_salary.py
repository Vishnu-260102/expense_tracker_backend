# Generated by Django 4.1.7 on 2023-09-28 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('expense_track', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='expensedetails',
            name='monthly_salary',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.PROTECT, to='expense_track.monthlysalary'),
            preserve_default=False,
        ),
    ]
