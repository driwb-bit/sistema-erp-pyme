from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction # Para que si falla algo, no guarde nada a medias
from django.contrib import messages
from .forms import VentaForm, DetalleVentaFormSet
from django.http import JsonResponse
from inventario.models import Producto
from .models import Venta
from django.db.models import Q # <--- IMPORTANTE: AGREGAR ESTO AL PRINCIPIO


DATOS_EMPRESA = {
    "nombre": "MI NEGOCIO",
    "direccion": "Calle Falsa 123, Resistencia",
    "telefono": "3624-000000",
    "cuit": "20-12345678-9",
    "mensaje_pie": "¡Gracias por su compra!",
    "nota_legal": "DOCUMENTO NO VÁLIDO COMO FACTURA"
}

@login_required
def crear_venta(request):
    if request.method == 'POST':
        form_venta = VentaForm(request.POST)
        formset_detalle = DetalleVentaFormSet(request.POST)

        if form_venta.is_valid() and formset_detalle.is_valid():
            try:
                with transaction.atomic():
                    # 1. Guardar la Venta (Padre)
                    venta = form_venta.save(commit=False)
                    venta.usuario = request.user
                    
                    # --- NUEVO: CAPTURAR EL MÉTODO DE PAGO ---
                    # El input hidden en el HTML se llama 'metodo_pago_seleccionado'
                    metodo = request.POST.get('metodo_pago_seleccionado', 'EFECTIVO')
                    venta.metodo_pago = metodo
                    
                    venta.save()

                    # 2. Guardar los Detalles (Hijos)
                    detalles = formset_detalle.save(commit=False)
                    for detalle in detalles:
                        detalle.venta = venta
                        detalle.save()
                    
                    messages.success(request, '¡Venta registrada exitosamente!')
                    
                    # --- NUEVO: REDIRIGIR AL TICKET EN LUGAR DEL HOME ---
                    return redirect('ticket_venta', venta_id=venta.id)

            except Exception as e:
                messages.error(request, f"Error al guardar: {e}")
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        # Si es GET (entrar a la página), mostramos formularios vacíos
        form_venta = VentaForm()
        formset_detalle = DetalleVentaFormSet()

    return render(request, 'ventas/nueva_venta.html', {
        'form_venta': form_venta,
        'formset_detalle': formset_detalle
    })

def buscar_producto_api(request):
    codigo = request.GET.get('codigo', None)
    producto_id = request.GET.get('id', None) # <--- Ahora aceptamos ID
    
    data = {'encontrado': False}
    
    try:
        producto = None
        
        # Estrategia 1: Buscar por Código de Barras (Escáner)
        if codigo:
            producto = Producto.objects.get(codigo=codigo)
            
        # Estrategia 2: Buscar por ID (Lista desplegable manual)
        elif producto_id:
            producto = Producto.objects.get(id=producto_id)
            
        if producto:
            data = {
                'encontrado': True,
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'stock': producto.stock_actual
            }
    except (Producto.DoesNotExist, ValueError):
        # ValueError captura si mandan un ID que no es número
        data = {'encontrado': False}
    
    return JsonResponse(data)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction # Para que si falla algo, no guarde nada a medias
from django.contrib import messages
from .forms import VentaForm, DetalleVentaFormSet
from django.http import JsonResponse
from inventario.models import Producto
from .models import Venta

DATOS_EMPRESA = {
    "nombre": "MI NEGOCIO",
    "direccion": "Calle Falsa 123, Resistencia",
    "telefono": "3624-000000",
    "cuit": "20-12345678-9",
    "mensaje_pie": "¡Gracias por su compra!",
    "nota_legal": "DOCUMENTO NO VÁLIDO COMO FACTURA"
}

@login_required
def crear_venta(request):
    if request.method == 'POST':
        form_venta = VentaForm(request.POST)
        formset_detalle = DetalleVentaFormSet(request.POST)

        if form_venta.is_valid() and formset_detalle.is_valid():
            try:
                with transaction.atomic():
                    # 1. Guardar la Venta (Padre)
                    venta = form_venta.save(commit=False)
                    venta.usuario = request.user
                    
                    # --- NUEVO: CAPTURAR EL MÉTODO DE PAGO ---
                    # El input hidden en el HTML se llama 'metodo_pago_seleccionado'
                    metodo = request.POST.get('metodo_pago_seleccionado', 'EFECTIVO')
                    venta.metodo_pago = metodo
                    
                    venta.save()

                    # 2. Guardar los Detalles (Hijos)
                    detalles = formset_detalle.save(commit=False)
                    for detalle in detalles:
                        detalle.venta = venta
                        detalle.save()
                    
                    messages.success(request, '¡Venta registrada exitosamente!')
                    
                    # --- NUEVO: REDIRIGIR AL TICKET EN LUGAR DEL HOME ---
                    return redirect('ticket_venta', venta_id=venta.id)

            except Exception as e:
                messages.error(request, f"Error al guardar: {e}")
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        # Si es GET (entrar a la página), mostramos formularios vacíos
        form_venta = VentaForm()
        formset_detalle = DetalleVentaFormSet()

    return render(request, 'ventas/nueva_venta.html', {
        'form_venta': form_venta,
        'formset_detalle': formset_detalle
    })

def buscar_producto_api(request):
    query = request.GET.get('codigo', None) # Le llamamos 'query' porque puede ser cualquier cosa
    producto_id = request.GET.get('id', None)
    
    data = {'encontrado': False}
    
    try:
        producto = None
        
        # ESTRATEGIA MEJORADA:
        if query:
            # Buscamos si coincide con el Código Interno O con el Código de Barras
            # Q(campo__iexact=valor) hace que no importen mayúsculas/minúsculas
            producto = Producto.objects.filter(
                Q(codigo__iexact=query) | Q(codigo_barra__iexact=query)
            ).first() # Usamos .first() por si las dudas, aunque deberían ser únicos
            
        elif producto_id:
            producto = Producto.objects.get(id=producto_id)
            
        if producto:
            data = {
                'encontrado': True,
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'stock': producto.stock_actual,
                'codigo': producto.codigo # Devolvemos el interno para mostrar
            }
    except Exception as e:
        print(f"Error buscando producto: {e}")
        data = {'encontrado': False}
    
    return JsonResponse(data)

def ticket_venta(request, venta_id):
    try:
        # Buscamos la venta por su ID
        venta = Venta.objects.get(id=venta_id)
        
        # Obtenemos los productos vendidos
        detalles = venta.detalles.all() 
        
        context = {
            'venta': venta,
            'detalles': detalles,
            'empresa': DATOS_EMPRESA, # Pasamos los datos de configuración
        }
        return render(request, 'ventas/ticket.html', context)

    except Venta.DoesNotExist:
        messages.error(request, "La venta solicitada no existe.")
        return redirect('crear_venta')
    


