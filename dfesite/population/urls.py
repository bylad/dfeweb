from django.urls import path
from population import views

app_name = 'population'

urlpatterns = [
    path('', views.PopulationListView.as_view(), name='list'),
    path('<int:pk>/', views.PopulationDetailView.as_view(), name='migr_detail'),
    path('success/', views.pptx, name='success'),
]
