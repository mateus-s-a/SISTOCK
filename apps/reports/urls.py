from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportIndexView.as_view(), name='report_index'),
    path('stock/', views.StockReportView.as_view(), name='stock_report'),
    path('movements/', views.MovementReportView.as_view(), name='movement_report'),
    path('export/stock/', views.export_stock_csv, name='export_stock_csv'),
    path('export/movements/', views.export_movements_csv, name='export_movements_csv'),

    path('users/', views.UserReportView.as_view(), name='user_report'),
]
