from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('check_point',views.check_point,name='check_point')
]
