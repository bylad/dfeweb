from django.urls import path
from . import views

app_name = 'rate'

urlpatterns = [
    path('', views.DailyListView.as_view(), name='daily_list'),
    path('monthly/', views.MonthlyListView.as_view(), name='monthly_list'),
    path('chart', views.ChartView.as_view(), name='chart'),
    path('success/', views.xlsx, name='success'),
]
