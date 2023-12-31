# Generated by Django 4.1.7 on 2023-09-28 07:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserOTP',
            fields=[
                ('id_otp', models.BigAutoField(primary_key=True, serialize=False)),
                ('email_id', models.EmailField(max_length=254)),
                ('otp_code', models.CharField(max_length=6)),
                ('creation_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('expiry', models.DateTimeField()),
                ('otp_for', models.CharField(choices=[('0', 'Password Reset OTP'), ('1', 'Profile Email Change OTP'), ('2', 'Email Verify OTP')], max_length=1)),
            ],
            options={
                'db_table': 'user_otp',
            },
        ),
        migrations.RemoveConstraint(
            model_name='user',
            name='Admin and Customer values cannot be same',
        ),
        migrations.RemoveConstraint(
            model_name='user',
            name='Customer cannot become a staff',
        ),
        migrations.RemoveConstraint(
            model_name='user',
            name='Customer cannot become superuser',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_adminuser',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_customer',
        ),
        migrations.AddField(
            model_name='user',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userotp',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='otp_set', to=settings.AUTH_USER_MODEL),
        ),
    ]
