from django.contrib import admin
from .models import Categoria, Producto, MovimientoStock

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'categoria', 'precio', 'stock_actual', 'stock_minimo')
    list_filter = ('categoria',) # Filtro lateral
    search_fields = ('nombre', 'codigo') # Barra de búsqueda
    # Hacemos que stock_actual sea solo lectura para obligar a usar "Movimientos"
    readonly_fields = ('stock_actual',) 
    search_help_text = "Busca por nombre o código"

class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'producto', 'tipo', 'cantidad', 'usuario')
    list_filter = ('tipo', 'fecha')
    
    # Al crear un movimiento desde el admin, asignamos el usuario logueado automáticamente
    def save_model(self, request, obj, form, change):
        if not obj.usuario:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Categoria)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(MovimientoStock, MovimientoStockAdmin)
