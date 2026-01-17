from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from inventario.models import Producto 
# Nota: Ya no necesitamos importar MovimientoStock aquí porque lo manejamos en la View

class Venta(models.Model):
    METODOS_PAGO = [
        ('EFECTIVO', 'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('DEBITO', 'Tarjeta de Débito'),
        ('CREDITO', 'Tarjeta de Crédito'),
        ('QR', 'QR / Billetera Virtual'),
        ('OTRO', 'Otro'),
    ]

    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    cliente = models.CharField(max_length=100, default="Consumidor Final")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    metodo_pago = models.CharField(
        max_length=20, 
        choices=METODOS_PAGO, 
        default='EFECTIVO'
    )

    def __str__(self):
        return f"Venta #{self.pk} - {self.fecha.strftime('%d/%m/%Y')}"

    def calcular_total(self):
        # Suma todos los subtotales de los detalles hijos y actualiza la cabecera
        total = sum(item.subtotal for item in self.detalles.all())
        self.total = total
        self.save()

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    
    # Estos campos son útiles para congelar el precio histórico
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # SOLO calculamos precios, NO tocamos el stock (eso lo hace la View)
        if not self.pk:
            self.precio_unitario = self.producto.precio 
            self.subtotal = self.cantidad * self.precio_unitario
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

# --- ESTA ES LA CLASE QUE FALTABA PARA LA CAJA ---
class Gasto(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    descripcion = models.CharField(max_length=200, help_text="Ej: Pago al sodero, Limpieza, etc.")
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"${self.monto} - {self.descripcion}"