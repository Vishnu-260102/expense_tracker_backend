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

from .models import MonthlySalary, ExpenseDetails
from .serializers import MonthlySalarySerializer, ExpenseDetailsSerializer


class MonthlySalaryView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    queryset = MonthlySalary.objects.all()
    serializer_class = MonthlySalarySerializer

    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)


class ExpenseDetailsView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    queryset = ExpenseDetails.objects.all()
    serializer_class = ExpenseDetailsSerializer

    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)
