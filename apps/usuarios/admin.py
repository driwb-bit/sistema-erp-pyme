from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class UsuarioAdmin(UserAdmin):
    # Mostramos nuestros campos personalizados en la lista de usuarios
    list_display = ('username', 'email', 'rol', 'is_staff')
    list_filter = ('rol', 'is_staff', 'is_active')
    
    # Agregamos nuestros campos al formulario de edición de usuario
    # 'fieldsets' controla el formulario de "Editar Usuario"
    fieldsets = UserAdmin.fieldsets + (
        ('Información Extra', {'fields': ('rol', 'telefono', 'direccion')}),
    )
    
    # 'add_fieldsets' controla el formulario de "Crear Usuario"
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Extra', {'fields': ('rol', 'telefono', 'direccion')}),
    )

admin.site.register(Usuario, UsuarioAdmin)