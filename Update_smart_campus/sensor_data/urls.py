from django.urls import path
from . import views

urlpatterns = [
    path('', views.sensor_data_list, name='sensor_data_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('event-data/', views.event_data, name='event_data'),
    path('data-analysis/', views.data_analysis, name='data_analysis'),
]