from datetime import datetime, timedelta
from random import randint
from django.conf import settings
from django.forms import model_to_dict
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from knox.models import AuthToken
from rest_framework import generics, status
from django.db import IntegrityError
from django.utils import timezone
from django.db.models import Q, ProtectedError
from models_logging.models import Change
from django.utils.timezone import utc
from django.http import Http404
from django.core.mail import send_mail
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from cryptography.fernet import Fernet, InvalidToken
from django.template.loader import render_to_string
import dotenv
import os
from django.contrib.auth.hashers import make_password


# local imports
from custom.permissions import isAdmin, isSuperuser
from accounts.models import Admin, AdminOTP, User
from accounts.serializers import AdminSignInSerializer

#
dotenv.load_dotenv()
#
fernet = Fernet(os.getenv('crypt_key'))
#


class AdminSignInView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = AdminSignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        token_obj, token = AuthToken.objects.create(user=user)
        expiry = timezone.localtime(token_obj.expiry)
        User.objects.filter(id=user.id).update(
            last_login=datetime.now(tz=timezone.utc))
        if user.admin.admin_email_verified:
            email_verified = True
        else:
            email_verified = False
        return Response({"success": True, "message": "Login Successful", "email_verified": email_verified, "token": token, "login_expiry": expiry, "preferences": {}})


# Check Token Valid:
class CheckTokenAPI(generics.GenericAPIView):
    def get(self, request):
        if request.user.admin.admin_email_verified == False:
            return Response({"success": False, "message": "Verify Email Address"})
        return Response({"success": True, "message": "User already logged in"})


# Get Admin user info:
class AdminInfo(generics.GenericAPIView):
    permission_classes = [isAdmin]

    def post(self, request, *args, **kwargs):
        try:
            admin = Admin.objects.get(user=request.user)
        except Admin.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        # if admin.admin_email_verified == False:
        #     return Response({"error_detail": ['Admin User need to verify email first']}, status=status.HTTP_403_FORBIDDEN)
        expiry = timezone.localtime(AuthToken.objects.get(
            token_key=request.auth.token_key).expiry)
        data = {"user": {"username": request.user.username, "admin_name": admin.name,
                         "admin_email": request.user.email,
                         "login_expiry": expiry, "admin_email_verified": admin.admin_email_verified}}
        return Response({"data": data})


# Admin Change Password API:
class AdminChangePassword(generics.GenericAPIView):
    permission_classes = [isAdmin]

    def post(self, request, *args, **kwargs):
        user = (request.user)
        if (request.data['old_password'] == request.data['new_password']):
            return Response({"error_detail": ['New Password and Old password cant be same']}, status=status.HTTP_400_BAD_REQUEST)
        if bool(user.check_password(request.data['old_password'])) == False:
            return Response({"error_detail": ['Incorrect password entered as Current Password']}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(request.data['new_password'])
        user.save()
        # Delete all  Tokens of this user to logout from other Devices other than This Device/Browser --
        AuthToken.objects.filter(user=user).exclude(
            token_key=request.auth.token_key).delete()
        return Response({"message": "Password changed successfully"})


# Update Admin by self
class AdminChange(generics.GenericAPIView):
    permission_classes = [isAdmin]

    def post(self, request, *args, **kwargs):
        user = (request.user)
        data = request.data.copy()
        request.data.pop('email')

        # Case - When OTP is entered with other data to  save email
        if ('email_otp' in request.data):
            # Delete Expired OTPs of all users.  || Later:  Need to check case of Valid OTPs of this User other than email in request
            AdminOTP.objects.filter(expiry__lt=timezone.now()).delete()
            ##
            try:
                latest_otp = AdminOTP.objects.filter(
                    admin=request.user.admin, email_id=data['email'], otp_for=1, expiry__gte=timezone.now()).latest('creation_time')
                if (latest_otp.otp_code == request.data['email_otp']):
                    try:
                        user.email = data['email']
                        user.save()
                    except IntegrityError:
                        return Response({"error_detail": ['Email already associated with another account']}, status=status.HTTP_400_BAD_REQUEST)
                    request.user.admin.name = request.data['name']
                    request.user.admin.save()
                    # Delete this OTP because its usage is over.
                    latest_otp.delete()
                    # Delete OTP related with user & email
                    AdminOTP.objects.filter(
                        admin=request.user.admin, email_id=data['email']).delete()  # / mutli request scenario
                    return Response({"success": True, 'message': "Profile updated with email being successfully verified"})
                else:
                    raise AdminOTP.DoesNotExist
            except AdminOTP.DoesNotExist:
                return Response({"error_detail": ['OTP entered is incorrect']}, status=status.HTTP_400_BAD_REQUEST)

        # Case - When Email is changed... OTP is sent to verify the email
        if (user.email != data['email']):
            if User.objects.filter(
                    email=data['email']).exclude(id=user.pk).exists():
                return Response({"error_detail": ['Email already associated with another account']}, status=status.HTTP_400_BAD_REQUEST)

            otp = (randint(100000, 999999))
            message = f'\n{request.user.admin.name}, \n We received a request to update your email on the Jewellery Association Admin. Please use the OTP {otp} to verify this email and complete the process.OTP is valid for 2 minutes only.'
            subject = "One Time Password to Verify your Email Address"
            # MODE - WHEN EMAIL IS CHANGED by SELF- OTP is sent
            AdminOTP.objects.create(admin=request.user.admin, otp_code=otp,
                                    expiry=timezone.now() + timedelta(minutes=2), email_id=data['email'], otp_for=1)
            html_message = render_to_string('verify_email_otp.html', {
                "name": request.user.admin.name, "code": otp})
            send_mail(subject=subject, message=message, html_message=html_message,
                      from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[data['email']])
            return Response({"success": True, "message": "Email verification Required"}, status=status.HTTP_200_OK)

        # Case - When Only Admin Name is Changed
        request.user.admin.name = request.data['name']
        request.user.admin.save()
        return Response({"success": True, "message": "Profile Updated"}, status=status.HTTP_200_OK)


# Create Admin OTP:
class AdminOTPCreate(generics.GenericAPIView):
    permission_classes = [isAdmin]

    def post(self, request, *args, **kwargs):
        email = request.data['email']
        otp_for = request.data['otp_for']
        try:
            EmailValidator()(email)
        except ValidationError:
            return Response({"error_detail": ['Invalid email format']}, status=status.HTTP_400_BAD_REQUEST)
        if (User.objects.filter(Q(email=email)).exclude(id=request.user.id).exists()):
            return Response({"error_detail": ['Email already associated with another account']}, status=status.HTTP_400_BAD_REQUEST)
        otp = (randint(100000, 999999))
        # MODE - CREATE ADMIN OTP - now for Email verification for superadmin changed mail - / 1. profile change / 2.verification
        AdminOTP.objects.create(otp_for=otp_for, admin=request.user.admin, otp_code=otp,
                                expiry=timezone.now() + timedelta(minutes=2), email_id=email)
        message = f'\n{request.user.admin.name}, \n We received a request to update your email on the Jewellery Association Admin. Please use the OTP {otp} to verify this email and complete the process.OTP is valid for 2 minutes only.'
        html_message = render_to_string('verify_email_otp.html', {
                                        "name": request.user.admin.name, "code": otp})
        subject = "One Time Password to Verify your Email Address"
        send_mail(html_message=html_message, subject=subject, message=message,
                  from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[email])
        return Response({'message': "OTP created and is sent to your email"})


# Verify Admin OTP:
class AdminOTPVerify(generics.GenericAPIView):
    permission_classes = [isAdmin]

    def post(self, request, *args, **kwargs):
        if 'email_otp' in request.data:
            # Delete Expired OTPs of all users.  || Later:  Need to check case of Valid OTPs of this User other than email in request
            AdminOTP.objects.filter(expiry__lt=timezone.now()).delete()
            try:
                # otp  for  -- "2", "Email Verify OTP" - change if any other scenario uses this API view
                latest_otp = AdminOTP.objects.filter(
                    admin=request.user.admin, otp_for=2, email_id=request.data['email'], expiry__gte=timezone.now()).latest('creation_time')
                if (latest_otp.otp_code == request.data['email_otp']):
                    request.user.admin.admin_email_verified = True
                    request.user.admin.save()
                    # Delete this OTP because its usage is over.
                    latest_otp.delete()
                    # Delete OTP related with user & email
                    AdminOTP.objects.filter(
                        admin=request.user.admin, email_id=request.data['email']).delete()  # / mutli request scenario
                    return Response({'message': "OTP verified"})
                else:
                    raise AdminOTP.DoesNotExist
            except AdminOTP.DoesNotExist:
                return Response({"error_detail": ['OTP entered is incorrect']}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error_detail": ['Invalid Request']}, status=status.HTTP_400_BAD_REQUEST)


# Reset Admin Password:
class AdminResetPassword(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if 'reset_password' in request.data:
            try:
                try:
                    EmailValidator()(request.data['user'])
                    user = User.objects.filter(is_adminuser=True).get(
                        email=request.data['user'])
                except:
                    user = User.objects.filter(is_adminuser=True).get(
                        username=request.data['user'])
                #
                # check if already a reset link/otp request exists with expiry time still left
                if (AdminOTP.objects.filter(admin=user.admin, otp_for=0, email_id=user.email, expiry__gt=timezone.now()).exists()):
                    return Response({"error_detail": ["A valid reset link already exists. Please use it / wait till its expiry"]}, status=status.HTTP_400_BAD_REQUEST)
                #
                subject = "Link to reset your Password"
                origin = request.data['origin']
                OTP_code = randint(100000, 999999)
                encOTP = fernet.encrypt(str(OTP_code).encode())
                # MODE - ADMIN PASSWORD RESET / FORGOT
                AdminOTP.objects.create(admin=user.admin, otp_for=0, email_id=user.email,
                                        otp_code=OTP_code, expiry=timezone.now()+timedelta(minutes=5))
                message = f"Visit this link to confirm your willingness to reset your password and to enter new password : \n {origin}/auth-reset/confirm_reset/{encOTP.decode()} . \n This link is valid for next 5 minutes only"
                html_message = render_to_string(
                    'reset_email_template.html', {'origin': origin, "encOTP": encOTP, "name": user.admin.name, "account_type": "Admin", "path": "auth-reset/confirm_reset"})
                send_mail(subject=subject, message=message,
                          from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[user.email], html_message=html_message)
                # delete old OTPs created for passsword reset
                AdminOTP.objects.filter(
                    admin=user.admin,  otp_for=0, expiry__lt=timezone.now()).delete()
                return Response({"success": True, "message": "Email with reset link has been sent"})
            except User.DoesNotExist:
                return Response({"error_detail": ["No User Found with provided details"]}, status=status.HTTP_400_BAD_REQUEST)
        if 'change_password' in request.data:
            # passing invalid OTP/encrypted code ... / if code is malfunctioned
            try:
                decOTP = fernet.decrypt(
                    request.data['reset_code'].encode('utf-8')).decode()
            except InvalidToken:
                return Response({"error_detail": ["Invalid password reset link. Please request reset link again "]}, status=status.HTTP_400_BAD_REQUEST)
            #
            if (AdminOTP.objects.filter(otp_code=decOTP, otp_for=0,
                                        expiry__gte=timezone.now()).exists()):
                instance = AdminOTP.objects.get(otp_code=decOTP)
                user = instance.admin.user
                user.set_password(request.data['passwd'])
                user.save()
                # delete used OTP:
                instance.delete()
                # Delete users all tokens:
                AuthToken.objects.filter(user=user).delete()
                return Response({"success": True, 'message': "Password is reset successfully"})
            return Response({"error_detail": ["Invalid/Expired link used. Please request reset link again"]}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error_detail": []}, status=status.HTTP_400_BAD_REQUEST)


