from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    # Definimos los roles como constantes para evitar errores de dedo ("magic strings")
    ADMINISTRADOR = 1
    VENDEDOR = 2
    
    ROLES_CHOICES = (
        (ADMINISTRADOR, 'Administrador / Dueño'),
        (VENDEDOR, 'Vendedor'),
    )
    
    # Campos personalizados
    rol = models.PositiveSmallIntegerField(choices=ROLES_CHOICES, default=VENDEDOR)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    # Estos métodos nos ayudarán mucho en los templates HTML más adelante
    # Ej: {% if request.user.es_admin %} ... {% endif %}
    @property
    def es_admin(self):
        return self.rol == self.ADMINISTRADOR

    @property
    def es_vendedor(self):
        return self.rol == self.VENDEDOR

    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"
