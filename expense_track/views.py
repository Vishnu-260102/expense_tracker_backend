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

from .models import MonthlySalary, ExpenseDetails, CreditDetails
from .serializers import MonthlySalarySerializer, ExpenseDetailsSerializer, CreditDetailsSerializer


class MonthlySalaryView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    queryset = MonthlySalary.objects.all()
    serializer_class = MonthlySalarySerializer

    def get(self, request, *args, **kwargs):
        data = {}
        output = []
        current_month = datetime.now().strftime("%B")
        current_year = datetime.now().strftime("%Y")
        # monthly_salary = MonthlySalary.objects.filter(
        #         year=current_year).get(month=current_month)
        # data.update()

        try:
            # monthly_salary = MonthlySalary.objects.filter(
            #     year=current_year,month=current_month)
            monthly_salary = MonthlySalary.objects.filter(
                year=current_year, user=request.user.pk).get(month=current_month)
            serializer = self.get_serializer(monthly_salary, many=True)
            data.update({"id": monthly_salary.pk,
                        "amount": monthly_salary.salary})
            output.append(data)

        except MonthlySalary.DoesNotExist:
            data.update({"amount": "No salary added for current month"})
            # return Response({"message": "No salary added"})
            output.append(data)
        return Response(output, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        request.data.update({"user": request.user.pk})
        if (MonthlySalary.objects.filter(month=request.data['month']).exists()):
            if (MonthlySalary.objects.filter(year=request.data['year'], user=request.user.pk).exists()):
                return Response({"message": "This month salary has been already Updated"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = MonthlySalarySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CurrentExpenseDetailsView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    queryset = ExpenseDetails.objects.all()
    serializer_class = ExpenseDetailsSerializer

    def get(self, request, *args, **kwargs):
        if 'month' in request.query_params and 'year' in request.query_params:
            queryset = ExpenseDetails.objects.filter(
                month=request.query_params['month'], year=request.query_params['year'], user=request.user.pk)
            serializer = ExpenseDetailsSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK)

    def post(self, request, *args, **Kwargs):
        instance = {}
        try:
            monthly_salary = MonthlySalary.objects.filter(
                year=request.data['year']).get(month=request.data['month'], user=request.user.pk)
            instance.update({"monthly_salary": monthly_salary.pk})
            instance.update({"month": request.data['month'], "year": request.data['year'], "expense_name": request.data['expense_name'],
                             "expense_description": request.data['expense_description'], "expense_date": request.data['expense_date'],
                             "amount": request.data['amount'], "user": request.user.pk})
            print(instance)
            serializer = ExpenseDetailsSerializer(data=instance)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except MonthlySalary.DoesNotExist:
            return Response({"message": "No salary found for corresponding month and year"})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CurrentCreditDetailsView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    queryset = CreditDetails.objects.all()
    serializer_class = CreditDetailsSerializer

    # def get(self, request, *args, **kwargs):
    #     if 'month' in request.query_params and 'year' in request.query_params:
    #         queryset = ExpenseDetails.objects.filter(
    #             month=request.query_params['month'], year=request.query_params['year'], user=request.user.pk)
    #         serializer = ExpenseDetailsSerializer(queryset, many=True)
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(status=status.HTTP_200_OK)

    def post(self, request, *args, **Kwargs):
        instance = {}
        try:
            monthly_salary = MonthlySalary.objects.filter(
                year=request.data['year']).get(month=request.data['month'], user=request.user.pk)
            instance.update({"monthly_salary": monthly_salary.pk})
            instance.update({"month": request.data['month'], "year": request.data['year'], "credit_name": request.data['credit_name'],
                             "credit_description": request.data['credit_description'], "credit_date": request.data['credit_date'],
                             "amount": request.data['amount'], "user": request.user.pk})
            print(instance)
            serializer = CreditDetailsSerializer(data=instance)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except MonthlySalary.DoesNotExist:
            return Response({"message": "No salary found for corresponding month and year"})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CurrentReportView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        if 'month' in request.query_params and 'year' in request.query_params:
            output = []
            instance = {}
            if (MonthlySalary.objects.filter(
                    year=request.query_params['year'], month=request.query_params['month'], user=request.user.pk).exists()):
                monthly_salary = MonthlySalary.objects.filter(
                    year=request.query_params['year']).get(month=request.query_params['month'], user=request.user.pk)
                instance.update(
                    {"name": "Salary", "salary_amount": monthly_salary.salary,
                     "date": monthly_salary.salary_date, "description": request.query_params['month']+" "+"Salary"})
                if instance not in output:
                    output.append(instance)
            exp_queryset = ExpenseDetails.objects.filter(
                month=request.query_params['month'], year=request.query_params['year'], user=request.user.pk)
            exp_serializer = ExpenseDetailsSerializer(exp_queryset, many=True)
            cred_queryset = CreditDetails.objects.filter(
                month=request.query_params['month'], year=request.query_params['year'], user=request.user.pk)
            cred_serializer = CreditDetailsSerializer(cred_queryset, many=True)

            for exp_data in exp_serializer.data:
                exp_instance = {}
                exp_instance.update({"name": exp_data['expense_name'], "description": exp_data['expense_description'],
                                     "date": exp_data['expense_date'], "exp_amount": exp_data['amount']})
                if exp_instance not in output:
                    output.append(exp_instance)

            for cred_data in cred_serializer.data:
                cred_instance = {}
                cred_instance.update({"name": cred_data['credit_name'], "description": cred_data['credit_description'],
                                     "date": cred_data['credit_date'], "cred_amount": cred_data['amount']})
                if cred_instance not in output:
                    output.append(cred_instance)
            return Response(output, status=status.HTTP_200_OK)


class CalcData:
    def __init__(self, cred_tot, exp_tot):
        self.cred_tot = cred_tot
        self.exp_tot = exp_tot

    def get_entry(self):
        return "{0} by {1}".format(self.cred_tot, self.exp_tot)


class HistoryReportView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        output = []
        all_salary_ids = []
        curr_salary_id = []
        salary_ids = []
        current_month = datetime.now().strftime("%B")
        current_year = datetime.now().strftime("%Y")
        current_month_id = MonthlySalary.objects.filter(
            month=current_month, year=current_year, user=request.user.pk).get()

        curr_salary_id.append(current_month_id.id)
        monthly_salary = MonthlySalary.objects.filter(user=request.user.pk)
        monthly_salary_serializer = MonthlySalarySerializer(
            monthly_salary, many=True)
        for x in range(len(monthly_salary_serializer.data)):
            all_salary_ids.append(monthly_salary_serializer.data[x]['id'])
        for y in all_salary_ids:
            if y not in curr_salary_id:
                salary_ids.append(y)

        print(salary_ids)
        for data in salary_ids:
            instance = {}
            print(data)
            queryset = MonthlySalary.objects.filter(id=data)
            serializer = MonthlySalarySerializer(queryset, many=True)
            for month_data in serializer.data:
                cred = CreditDetails.objects.filter(
                    monthly_salary=month_data['id'])
                cred_serializer = CreditDetailsSerializer(cred, many=True)
                cred_total = 0
                for i in range(len(cred_serializer.data)):
                    cred_amnt = int(cred_serializer.data[i]['amount'])
                    cred_total += cred_amnt
                CalcData.cred_tot = cred_total

                exp = ExpenseDetails.objects.filter(
                    monthly_salary=month_data['id'])
                exp_serializer = ExpenseDetailsSerializer(exp, many=True)
                exp_total = 0
                for j in range(len(exp_serializer.data)):
                    exp_amnt = int(exp_serializer.data[j]['amount'])
                    exp_total += exp_amnt
                CalcData.exp_tot = exp_total

            instance.update(
                {"salary_id": month_data['id'], "month": month_data['month'], "year": month_data['year'], "salary": month_data['salary'],
                 "exp_total": CalcData.exp_tot, "cred_total": CalcData.cred_tot})
            if instance not in output:
                output.append(instance)
            print(CalcData.cred_tot)
            print(CalcData.exp_tot)
        return Response(output, status=status.HTTP_200_OK)
