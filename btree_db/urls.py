from django.urls import path
from . import views

app_name = 'btree_db'
urlpatterns = [
    path('', views.index, name='index'),
    path('insert/', views.insert, name='insert'),
    path('inserted/', views.inserted, name='inserted'),
    path('update/', views.update, name='update'),
    path('updated/', views.updated, name='updated'),
    path('delete/', views.delete, name='delete'),
    path('deleted/', views.deleted, name='deleted'),
    path('read/', views.read, name='read'),
    path('view/<int:key>', views.view, name='view'),
    path('delete_all/', views.delete_all, name='delete_all'),
    path('view_all/', views.view_all, name='view_all'),
]
