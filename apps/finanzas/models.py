from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import Coalesce # Ayuda a convertir "None" en "0"
from django.apps import apps # Para importar modelos sin errores circulares

class Arqueo(models.Model):
    ESTADO_CHOICES = (
        ('ABIERTA', 'Abierta'),
        ('CERRADA', 'Cerrada'),
    )

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    monto_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Lo que contaste físicamente en el cajón")
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='ABIERTA')
    
    # Auditoría
    total_ventas_sistema = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_salidas_sistema = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    diferencia = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # ... dentro de class Arqueo(models.Model): ...

    def cerrar_caja(self, monto_real):
        """Asigna los valores de cierre y guarda para disparar el cálculo."""
        self.monto_final = monto_real
        self.estado = 'CERRADA'
        # Al llamar a save(), se ejecutará toda la lógica matemática que escribimos antes
        self.save()
        
    def save(self, *args, **kwargs):
        # Si estamos CERRANDO la caja (cambio de estado a CERRADA y tenemos monto final)
        if self.estado == 'CERRADA' and self.monto_final is not None:
            if not self.fecha_cierre:
                self.fecha_cierre = timezone.now()

            # 1. Obtenemos el modelo de Venta dinámicamente
            Venta = apps.get_model('ventas', 'Venta')

            # 2. Sumamos todas las ventas (CORREGIDO)
            # Cambiamos 0.0 por 0 y agregamos output_field=models.DecimalField()
            ventas_turno = Venta.objects.filter(
                usuario=self.usuario,
                fecha__gte=self.fecha_apertura,
                fecha__lte=self.fecha_cierre
            ).aggregate(total=Coalesce(Sum('total'), 0, output_field=models.DecimalField()))
            
            self.total_ventas_sistema = ventas_turno['total']

            # 3. Sumamos todas las salidas (CORREGIDO)
            salidas_turno = self.salidas.aggregate(
                total=Coalesce(Sum('monto'), 0, output_field=models.DecimalField())
            )
            self.total_salidas_sistema = salidas_turno['total']

            # 4. Fórmula Maestra
            # Convertimos todo a float solo para la resta final matemática de Python
            dinero_esperado = float(self.monto_inicial) + float(self.total_ventas_sistema) - float(self.total_salidas_sistema)
            
            # 5. Calculamos la diferencia
            self.diferencia = float(self.monto_final) - dinero_esperado

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Caja {self.id} - {self.usuario} ({self.fecha_apertura.date()})"

class SalidaDinero(models.Model):
    arqueo = models.ForeignKey(Arqueo, on_delete=models.CASCADE, related_name='salidas')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"${self.monto} - {self.descripcion}"