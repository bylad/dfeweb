from django.urls import path
from subsidy import views

app_name = 'subsidy'

urlpatterns = [
    path('', views.SubsidyListView.as_view(), name='list'),
    path('<int:pk>/', views.SubsidyDetailView.as_view(), name='subsidy_detail'),
    path('success/', views.pptx, name='success'),
]
