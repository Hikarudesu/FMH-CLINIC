"""URL configuration for Reports & Analytics module."""

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Main Analytics Dashboard
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),

    # Dashboards
    path('finance/', views.finance_dashboard, name='finance_dashboard'),
    path('operations/', views.operations_dashboard, name='operations_dashboard'),

    # Sales Reports
    path('daily/', views.daily_sales_report, name='daily_sales_report'),
    path('sales/', views.sales_by_period, name='sales_by_period'),

    # Cash Drawer
    path('cash-drawer/', views.cash_drawer_report, name='cash_drawer_report'),

    # Finance Reports
    path('gross-profit/', views.gross_profit_report, name='gross_profit_report'),
    path('discounts/', views.discount_report, name='discount_report'),
    path('refunds/', views.refund_report, name='refund_report'),

    # Appointment Reports
    path('appointments/', views.appointment_reports, name='appointment_reports'),

    # Inventory Reports
    path('inventory/', views.inventory_reports, name='inventory_reports'),

    # Patient Reports
    path('patients/', views.patient_reports, name='patient_reports'),

    # Customer Reports
    path('customers/', views.customer_analytics, name='customer_analytics'),
    path('customer-list/', views.customer_list_report, name='customer_list_report'),

    # CSV Exports
    path('export/sales/', views.export_sales_csv, name='export_sales_csv'),
    path('export/daily/', views.export_daily_report_csv, name='export_daily_report_csv'),
]
