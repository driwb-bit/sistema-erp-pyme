from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
# IMPORTANTE: Traemos tu vista inteligente desde la app ventas
from ventas.views import home 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    
    # --- AQUÍ ESTABA EL ERROR ---
    # Antes usabas TemplateView (vacío). Ahora usamos 'home' (tu lógica).
    path('', home, name='home'), 
    
    path('reportes/', include('reportes.urls')),
    path('ventas/', include('ventas.urls')),
    path('inventario/', include('inventario.urls')),
    path('finanzas/', include('finanzas.urls')),
]