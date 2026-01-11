from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView # <--- Importar esto
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reportes/', include('reportes.urls')),
    path('', login_required(TemplateView.as_view(template_name='home.html')), name='home'),
    path('ventas/', include('ventas.urls')),
    path('inventario/', include('inventario.urls')),
    path('finanzas/', include('finanzas.urls')),
]
