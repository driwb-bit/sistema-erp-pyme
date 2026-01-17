from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction 
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, F, Count
from django.utils import timezone   

# Importamos los Forms y Modelos
from .forms import VentaForm, DetalleVentaFormSet, GastoForm
from inventario.models import Producto, MovimientoStock 
from .models import Venta, Gasto

DATOS_EMPRESA = {
    "nombre": "MI NEGOCIO",
    "direccion": "Calle Falsa 123, Resistencia",
    "telefono": "3624-000000",
    "cuit": "20-12345678-9",
    "mensaje_pie": "¡Gracias por su compra!",
    "nota_legal": "DOCUMENTO NO VÁLIDO COMO FACTURA"
}

# --- 1. DASHBOARD (HOME) ---
# apps/ventas/views.py

@login_required
def home(request):
    hoy = timezone.localtime(timezone.now()).date()
    
    context = {
        'total_ventas_hoy': 0,
        'cantidad_ventas_hoy': 0,
        'productos_bajo_stock': [],
        # Borramos 'debug_productos' porque ya no hace falta
    }

    # A. VENTAS (Solo Jefes)
    if request.user.is_staff:
        ventas_hoy = Venta.objects.filter(fecha__date=hoy)
        total = ventas_hoy.aggregate(Sum('total'))['total__sum']
        
        context['total_ventas_hoy'] = total if total else 0
        context['cantidad_ventas_hoy'] = ventas_hoy.count()

    # B. ALERTAS
    bajo_stock = Producto.objects.filter(
        stock_actual__lte=F('stock_minimo')
    ).order_by('stock_actual')[:10]
    
    context['productos_bajo_stock'] = bajo_stock

    return render(request, 'home.html', context)

# --- 2. NUEVA VENTA (CORREGIDO EL ERROR DE PRECIO) ---
@login_required
def crear_venta(request):
    if request.method == 'POST':
        form_venta = VentaForm(request.POST)
        formset_detalle = DetalleVentaFormSet(request.POST)

        if form_venta.is_valid() and formset_detalle.is_valid():
            try:
                with transaction.atomic():
                    # A. Guardar Cabecera
                    venta = form_venta.save(commit=False)
                    venta.usuario = request.user
                    venta.metodo_pago = request.POST.get('metodo_pago_seleccionado', 'EFECTIVO')
                    venta.save()

                    # B. Guardar Detalles
                    detalles = formset_detalle.save(commit=False)
                    total_acumulado = 0
                    
                    for detalle in detalles:
                        detalle.venta = venta
                        
                        # --- CORRECCIÓN DEL ERROR ---
                        # Usamos el precio del PRODUCTO original, ya que DetalleVenta no tiene campo precio
                        precio_real = detalle.producto.precio 
                        
                        # Calculamos subtotal
                        subtotal = detalle.cantidad * precio_real
                        total_acumulado += subtotal
                        
                        detalle.save()
                        
                        # C. Descontar Stock (Crear Movimiento)
                        MovimientoStock.objects.create(
                            producto=detalle.producto,
                            cantidad=detalle.cantidad,
                            tipo=MovimientoStock.SALIDA,
                            usuario=request.user,
                            observacion=f"Venta #{venta.id}"
                        )
                    
                    # D. Actualizar Total de la Venta
                    venta.total = total_acumulado
                    venta.save()
                    
                    messages.success(request, '¡Venta registrada exitosamente!')
                    return redirect('ticket_venta', venta_id=venta.id)

            except Exception as e:
                messages.error(request, f"Error al procesar la venta: {e}")
        else:
            messages.error(request, "Verifique los datos del formulario.")
    else:
        form_venta = VentaForm()
        formset_detalle = DetalleVentaFormSet()

    return render(request, 'ventas/nueva_venta.html', {
        'form_venta': form_venta,
        'formset_detalle': formset_detalle
    })

# --- 3. GESTIONAR CAJA Y GASTOS (LO QUE PEDISTE RESTAURAR) ---
@login_required
def gestionar_caja(request):
    hoy = timezone.localtime(timezone.now()).date()
    
    # Lógica para agregar Gasto
    if request.method == 'POST':
        form_gasto = GastoForm(request.POST)
        if form_gasto.is_valid():
            gasto = form_gasto.save(commit=False)
            gasto.usuario = request.user
            gasto.save()
            messages.success(request, "Gasto registrado correctamente.")
            return redirect('gestionar_caja')
    else:
        form_gasto = GastoForm()

    # Calcular Totales
    total_ventas = Venta.objects.filter(fecha__date=hoy).aggregate(Sum('total'))['total__sum'] or 0
    total_gastos = Gasto.objects.filter(fecha__date=hoy).aggregate(Sum('monto'))['monto__sum'] or 0
    
    # Desglose por método de pago
    resumen_pagos = Venta.objects.filter(fecha__date=hoy).values('metodo_pago').annotate(
        total=Sum('total'),
        cantidad=Count('id')
    )
    
    balance_final = total_ventas - total_gastos

    return render(request, 'ventas/gestionar_caja.html', {
        'fecha': hoy,
        'total_ventas': total_ventas,
        'total_gastos': total_gastos,
        'balance_final': balance_final,
        'resumen_pagos': resumen_pagos,
        'form_gasto': form_gasto,
        'lista_gastos': Gasto.objects.filter(fecha__date=hoy).order_by('-fecha')
    })

# --- 4. API Y TICKET (SIN CAMBIOS) ---
def buscar_producto_api(request):
    query = request.GET.get('codigo', None)
    producto_id = request.GET.get('id', None)
    data = {'encontrado': False}
    try:
        producto = None
        if query:
            producto = Producto.objects.filter(
                Q(codigo__iexact=query) | Q(codigo_barra__iexact=query)
            ).first()
        elif producto_id:
            producto = Producto.objects.get(id=producto_id)
            
        if producto:
            data = {
                'encontrado': True,
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'stock': producto.stock_actual,
                'codigo': producto.codigo 
            }
    except Exception:
        pass
    return JsonResponse(data)

def ticket_venta(request, venta_id):
    try:
        venta = Venta.objects.get(id=venta_id)
        detalles = venta.detalles.all() 
        context = {'venta': venta, 'detalles': detalles, 'empresa': DATOS_EMPRESA}
        return render(request, 'ventas/ticket.html', context)
    except Venta.DoesNotExist:
        return redirect('crear_venta')