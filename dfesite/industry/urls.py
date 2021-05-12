from django.urls import path
from industry import views

app_name = 'industry'

urlpatterns = [
    path('', views.IndustryNewsListView.as_view(), name='list'),
    path('<int:pk>/', views.IndustryNewsDetailView.as_view(), name='detail'),
    path('success/', views.pptx, name='success'),
]