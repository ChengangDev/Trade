from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^grids/', views.grids, name='grids'),
    url(r'^dayline/', views.dayline, name='dayline'),
]