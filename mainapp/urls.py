from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('news', views.news),
    path('visualization/', views.visualize_csv_form),
    path('data_download/', views.data_download),
    path('pred_show/', views.pred_show),
    path('predict', views.predict),
]