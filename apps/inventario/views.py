from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Producto

@login_required
def lista_productos(request):
    # Traemos todos los productos
    productos = Producto.objects.all().order_by('nombre')
    
    return render(request, 'inventario/lista_productos.html', {
        'productos': productos
    })
