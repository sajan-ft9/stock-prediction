from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('news', views.news),
    path('single_news/<str:link>', views.single_news)
]