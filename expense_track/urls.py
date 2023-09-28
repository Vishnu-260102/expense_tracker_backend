from django.urls import path

from .views import MonthlySalaryView, ExpenseDetailsView

urlpatterns = [
    path('monthly_salary', MonthlySalaryView.as_view(), name='monthly_salary'),
    path('expense_details', ExpenseDetailsView.as_view(), name='expense_details'),
]
