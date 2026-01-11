from django.urls import path
from .views import lista_productos

urlpatterns = [
    path('lista/', lista_productos, name='lista_productos'),
]