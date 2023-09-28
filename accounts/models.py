from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from . import file_save
from dateutil.relativedelta import relativedelta


# Accounts , access related models
# User model is used to store Users ; to be used as basic auth model for authentication of both admin and customers
class User(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_adminuser = models.BooleanField(default=False)
    account_expiry = models.DateField(blank=True, null=True)
    first_name = models.CharField(max_length=45, null=True, blank=True)
    last_name = models.CharField(max_length=45, null=True, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self) -> str:
        return 'User - ' + str(self.pk)

    LOGGING_IGNORE_FIELDS = ('password', 'first_name',
                             'last_name', 'last_login')

    class Meta:
        db_table = 'users'
        constraints = [
            models.CheckConstraint(violation_error_message='isAdmin and isCustomer values cannot be same', name='Admin and Customer values cannot be same', check=~(
                models.Q)(is_customer=models.F('is_adminuser'))),
            models.CheckConstraint(violation_error_message='Customer cannot become a staff',
                                   name='Customer cannot become a staff', check=~models.Q(models.Q(is_customer=True), models.Q(is_staff=True))),
            models.CheckConstraint(violation_error_message='Customer cannot become superuser',
                                   name='Customer cannot become superuser', check=~models.Q(models.Q(is_customer=True), models.Q(is_superuser=True))),
            models.CheckConstraint(
                check=models.Q(
                    username__regex=r'^\w(?:\w|[.-](?=\w))*$'
                ),
                name="Invalid username",
                violation_error_message="Username must only contain alphanumeric characters, '@', '#', '-', '_', and '.'",
            )
        ]


# Admin model is used to store Admin users
class Admin(models.Model):
    adminid = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=100)
    user = models.OneToOneField(
        'User', on_delete=models.PROTECT, limit_choices_to={'is_adminuser': True}, related_name='admin')
    admin_email_verified = models.BooleanField(default=False)

    def __str__(self) -> str:
        return 'Admin User - ' + str(self.pk)

    class Meta:
        db_table = 'admin'


# Admin OTP model is used to store Email OTPs of user
class AdminOTP(models.Model):

    OTP_FOR = (
        ("0", "Password Reset OTP"),
        ("1", "Profile Email Change OTP"),
        ("2", "Email Verify OTP"),
    )

    id_otp = models.BigAutoField(primary_key=True)
    admin = models.ForeignKey(
        'Admin', on_delete=models.CASCADE, related_name='otp_set')
    email_id = models.EmailField()
    otp_code = models.CharField(
        max_length=6)
    creation_time = models.DateTimeField(default=timezone.now)
    expiry = models.DateTimeField()
    otp_for = models.CharField(choices=OTP_FOR, max_length=1)

    def __str__(self) -> str:
        return 'Admin User OTP - ' + str(self.pk)

    class Meta:
        db_table = 'admin_otp'
    # LOG IGNORE THIS MODEL
