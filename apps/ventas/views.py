from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction # Para que si falla algo, no guarde nada a medias
from django.contrib import messages
from .forms import VentaForm, DetalleVentaFormSet

@login_required
def crear_venta(request):
    if request.method == 'POST':
        form_venta = VentaForm(request.POST)
        formset_detalle = DetalleVentaFormSet(request.POST)

        if form_venta.is_valid() and formset_detalle.is_valid():
            try:
                with transaction.atomic(): # Inicia bloque de seguridad
                    # 1. Guardar la Venta (Padre)
                    venta = form_venta.save(commit=False)
                    venta.usuario = request.user
                    venta.save()

                    # 2. Guardar los Detalles (Hijos)
                    detalles = formset_detalle.save(commit=False)
                    for detalle in detalles:
                        detalle.venta = venta
                        detalle.save() # Aquí se dispara tu lógica de descuento de stock
                    
                    messages.success(request, '¡Venta registrada exitosamente!')
                    return redirect('home')

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