from django.urls import path
from price import views

app_name = 'price'

urlpatterns = [
    path('', views.PriceListView.as_view(), name='list'),
    path('<int:pk>/', views.PriceDetailView.as_view(), name='price_detail'),
    path('success/', views.pptx, name='success'),
]
