from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from inventario.models import Producto, MovimientoStock # Importamos la otra app

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
        # Suma todos los subtotales de los detalles hijos
        total = sum(item.subtotal for item in self.detalles.all())
        self.total = total
        self.save()

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # 1. Si es un detalle nuevo, verificamos stock y congelamos precio
        if not self.pk:
            # Validar Stock
            if self.producto.stock_actual < self.cantidad:
                raise ValidationError(f"No hay suficiente stock de {self.producto.nombre}")
            
            # Congelar precio del momento
            self.precio_unitario = self.producto.precio # Asegúrate que tu Producto tenga campo 'precio' o 'precio_venta'
            self.subtotal = self.cantidad * self.precio_unitario

            # 2. AUTOMATIZACIÓN: Crear el Movimiento de Stock (Salida)
            # Esto descuenta el stock usando la lógica que hicimos en el paso anterior
            MovimientoStock.objects.create(
                producto=self.producto,
                cantidad=self.cantidad,
                tipo=MovimientoStock.SALIDA,
                usuario=self.venta.usuario,
                observacion=f"Venta #{self.venta.pk}"
            )

        super().save(*args, **kwargs)
        
        # 3. Actualizar el total de la venta padre
        self.venta.calcular_total()
