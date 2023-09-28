from django.utils import timezone
from django.db import models


class MonthlySalary(models.Model):
    id = models.AutoField(primary_key=True)
    month = models.CharField(max_length=20)
    year = models.CharField(max_length=5)
    salary = models.CharField(max_length=50)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return 'Monthly Salary - ' + str(self.pk)

    class Meta:
        db_table = 'monthly_salary'


class ExpenseDetails(models.Model):
    id = models.BigAutoField(primary_key=True)
    month = models.CharField(max_length=20)
    year = models.CharField(max_length=5)
    expense_name = models.CharField(max_length=100)
    expense_description = models.TextField()
    expense_date = models.DateField()
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return 'Expense Details - ' + str(self.pk)

    class Meta:
        db_table = 'expense_details'
