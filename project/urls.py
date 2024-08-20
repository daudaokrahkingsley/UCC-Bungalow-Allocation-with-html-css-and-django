from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('check_point',views.check_point,name='check_point'),
    path('manage-buildings/', views.admin_manage_buildings, name='manage_buildings'),
    path('get-buildings/', views.get_buildings, name='get_buildings'),
    path('view_all_preferences/', views.view_all_preferences, name='view_all_preferences'),
    path('delete_building/<int:building_id>/', views.delete_building, name='delete_building')
]
