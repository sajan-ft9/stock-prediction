from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('news', views.news),
    path('visualization/', views.visualize_csv_form),
    path('try/', views.visualize_csv, name='visualize_csv'),
]