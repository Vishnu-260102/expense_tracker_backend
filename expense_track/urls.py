from django.urls import path

from .views import MonthlySalaryView, CurrentExpenseDetailsView, CurrentCreditDetailsView, CurrentReportView, HistoryReportView

urlpatterns = [
    path('monthly_salary/', MonthlySalaryView.as_view(), name='monthly_salary'),
    path('expense_details/', CurrentExpenseDetailsView.as_view(), name='expense_details'),
    path('credit_details/', CurrentCreditDetailsView.as_view(), name='credit_details'),
    path('current_report/', CurrentReportView.as_view(), name='current_report'),
    path('history_report/', HistoryReportView.as_view(), name='history_report'),
]
