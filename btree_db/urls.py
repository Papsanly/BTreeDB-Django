from django.urls import path
from . import views

app_name = 'btree_db'
urlpatterns = [
    # Main page
    path('', views.index, name='index')
]
