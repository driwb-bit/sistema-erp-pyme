from django.urls import path
from .views import crear_venta
from . import views

urlpatterns = [
    path('nueva/', crear_venta, name='crear_venta'),
    path('api/buscar-producto/', views.buscar_producto_api, name='buscar_producto_api'),
    path('ticket/<int:venta_id>/', views.ticket_venta, name='ticket_venta'),
    path('caja/', views.gestionar_caja, name='gestionar_caja'),
]