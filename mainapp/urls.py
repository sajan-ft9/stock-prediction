from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('news', views.news),
    path('about', views.about),
    path('single_news/<int:id>', views.single_news)
]