from django.urls import path

from .views import MonthlySalaryView, CurrentExpenseDetailsView

urlpatterns = [
    path('monthly_salary/', MonthlySalaryView.as_view(), name='monthly_salary'),
    path('expense_details/', CurrentExpenseDetailsView.as_view(), name='expense_details'),
]
