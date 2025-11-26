from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('api/autocomplete/', views.MovementAutocompleteView.as_view(), name='movement_autocomplete'),

    path('movements/', views.MovementListView.as_view(), name='movement_list'),
    path('movements/add/', views.MovementCreateView.as_view(), name='movement_create'),
    path('movements/<int:pk>/', views.MovementDetailView.as_view(), name='movement_detail'),

    path('alerts/', views.StockAlertsView.as_view(), name='stock_alerts'),
]
