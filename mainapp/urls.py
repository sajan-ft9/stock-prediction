from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('news', views.news),
    path('visualization/', views.visualize_csv_form),
    path('data_download/', views.data_download),
    path('auto_download', views.auto_download),
    path('predict', views.predict),
    path('saved_predict', views.saved_predict),
    
]