from django.contrib import admin
from .models import Arqueo, SalidaDinero

class SalidaDineroInline(admin.TabularInline):
    model = SalidaDinero
    extra = 1

class ArqueoAdmin(admin.ModelAdmin):
    inlines = [SalidaDineroInline]
    list_display = ('id', 'usuario', 'fecha_apertura', 'estado', 'monto_inicial', 'monto_final', 'diferencia_calculada')
    readonly_fields = ('fecha_cierre', 'total_ventas_sistema', 'total_salidas_sistema', 'diferencia')
    list_filter = ('estado', 'fecha_apertura', 'usuario')

    def diferencia_calculada(self, obj):
        return obj.diferencia
    diferencia_calculada.short_description = "Diferencia (Sobra/Falta)"

    def save_model(self, request, obj, form, change):
        if not obj.usuario:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Arqueo, ArqueoAdmin)
admin.site.register(SalidaDinero)
