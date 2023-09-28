from rest_framework import serializers
from .models import MonthlySalary, ExpenseDetails


class MonthlySalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlySalary
        fields = '__all__'


class ExpenseDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseDetails
        fields = '__all__'
