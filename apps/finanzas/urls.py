from django.urls import path
from .views import gestionar_caja

urlpatterns = [
    path('caja/', gestionar_caja, name='gestionar_caja'),
]