from django.urls import path
from knox.views import LogoutView

from accounts.views import (AdminChange, AdminChangePassword, AdminInfo,
                            AdminOTPCreate, AdminOTPVerify, AdminResetPassword, AdminSignInView, CheckTokenAPI, )


urlpatterns = [
    path('auth/admin_signin/', AdminSignInView.as_view(), name='admin_sign_in'),
    path('auth/admin_signout/', LogoutView.as_view(), name='admin_sign_out'),
    path('auth/check_token/', CheckTokenAPI.as_view(),
         name='check_token_is_valid'),
    path('auth/admin_info/', AdminInfo.as_view(),
         name='get_admin_info'),
    path('admin_change_pass/', AdminChangePassword.as_view(),
         name='change_admin_pass'),
    path('admin_change/', AdminChange.as_view(), name='change_admin_details'),
    path('admin_create_otp/', AdminOTPCreate.as_view(),
         name='admin_create_otp'),
    path('admin_verify_otp/', AdminOTPVerify.as_view(),
         name='admin_verify_otp'),
    path('admin_reset_pass/', AdminResetPassword.as_view(),
         name='admin_reset_passwd'),
]
