from django.urls import path
from .views import crear_venta

urlpatterns = [
    path('nueva/', crear_venta, name='crear_venta'),
]