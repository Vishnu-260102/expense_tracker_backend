from rest_framework import serializers
from .models import MonthlySalary, ExpenseDetails, CreditDetails


class MonthlySalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlySalary
        fields = '__all__'


class ExpenseDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseDetails
        fields = '__all__'


class CreditDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditDetails
        fields = '__all__'
