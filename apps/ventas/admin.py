from django.contrib import admin
from django.utils.html import format_html # <--- Nuevo
from django.urls import reverse # <--- Nuevo
from .models import Venta, DetalleVenta

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    readonly_fields = ('precio_unitario', 'subtotal')
    autocomplete_fields = ['producto']

class VentaAdmin(admin.ModelAdmin):
    inlines = [DetalleVentaInline]
    list_display = ('id', 'fecha', 'cliente', 'total', 'usuario', 'acciones') # <--- Agregamos 'acciones'
    list_filter = ('fecha', 'usuario')
    readonly_fields = ('total', 'usuario')

    # ... Tus métodos save_model y save_formset déjalos igual ...
    def save_model(self, request, obj, form, change):
        if not getattr(obj, 'usuario', None):
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not hasattr(instance.venta, 'usuario') or not instance.venta.usuario:
                instance.venta.usuario = request.user
            instance.save()
        formset.save_m2m()

    # --- NUEVO: Botón para descargar Excel ---
    def acciones(self, obj):
        # Creamos un botón HTML que apunta a tu vista de exportación
        return format_html(
            '<a class="button" href="{}">Descargar Excel Global</a>',
            reverse('exportar_ventas')
        )
    acciones.short_description = "Reportes"
    acciones.allow_tags = True

admin.site.register(Venta, VentaAdmin)
