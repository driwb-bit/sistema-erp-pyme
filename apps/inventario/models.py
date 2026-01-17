from django.db import models
from django.conf import settings # Para importar tu modelo de Usuario correctamente
from django.core.exceptions import ValidationError

class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorías"

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    
    # 1. CODIGO INTERNO (SKU): Corto, para que vos lo escribas rápido si falla el escáner
    codigo = models.CharField(max_length=50, unique=True, help_text="Código interno (Ej: MAT-001)")
    
    # 2. CODIGO DE BARRAS (EAN): El que lee la pistola. Puede estar vacío (blank=True)
    codigo_barra = models.CharField(max_length=50, null=True, blank=True, unique=True, help_text="Escanee el código aquí")

    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    
    # Dinero
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Stock
    stock_actual = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5, help_text="Avisa cuando queda poco")
    
    def __str__(self):
        return f"{self.nombre} ({self.stock_actual})"

class MovimientoStock(models.Model):
    """
    Registra cada vez que entra o sale mercadería.
    """
    ENTRADA = 'ENTRADA'
    SALIDA = 'SALIDA'
    
    TIPO_CHOICES = (
        (ENTRADA, 'Entrada (Compra/Devolución)'),
        (SALIDA, 'Salida (Venta/Pérdida/Robo)'),
    )

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    observacion = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        # Lógica AUTOMÁTICA de actualización de stock
        # Solo ejecutamos esto si es un movimiento nuevo (no si lo estamos editando)
        if not self.pk: 
            if self.tipo == self.ENTRADA:
                self.producto.stock_actual += self.cantidad
            elif self.tipo == self.SALIDA:
                # Validación simple: no vender lo que no tienes
                if self.producto.stock_actual < self.cantidad:
                    raise ValidationError(f"No hay suficiente stock de {self.producto.nombre}")
                self.producto.stock_actual -= self.cantidad
            
            self.producto.save()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tipo} de {self.cantidad} - {self.producto.nombre}"