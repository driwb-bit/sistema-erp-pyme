from django.urls import path
from .views import reporte_ventas_excel

urlpatterns = [
    path('exportar/ventas/', reporte_ventas_excel, name='exportar_ventas'),
]