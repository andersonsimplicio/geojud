from typing import MappingView
from django.contrib import admin
from django.urls import path
from .views import IndexView,MapView

urlpatterns = [
    path('',IndexView.as_view(),name='index'),
    path('mapa',MapView,name='map'),
]
