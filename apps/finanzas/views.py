from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Arqueo, SalidaDinero

@login_required
def gestionar_caja(request):
    # Buscamos si hay una caja abierta para este usuario
    caja_abierta = Arqueo.objects.filter(usuario=request.user, estado='ABIERTA').last()

    if request.method == 'POST':
        accion = request.POST.get('accion')

        # CASO 1: ABRIR CAJA
        if accion == 'abrir':
            monto = request.POST.get('monto_inicial')
            Arqueo.objects.create(usuario=request.user, monto_inicial=monto, estado='ABIERTA')
            messages.success(request, 'Caja abierta correctamente.')
        
        # CASO 2: REGISTRAR GASTO (Salida)
        elif accion == 'gasto' and caja_abierta:
            monto = request.POST.get('monto_salida')
            desc = request.POST.get('descripcion')
            SalidaDinero.objects.create(arqueo=caja_abierta, monto=monto, descripcion=desc)
            messages.warning(request, 'Gasto registrado.')

        # CASO 3: CERRAR CAJA
        elif accion == 'cerrar' and caja_abierta:
            monto_real = request.POST.get('monto_final')
            caja_abierta.cerrar_caja(monto_real) # Usamos el método que creamos en el modelo
            messages.info(request, 'Caja cerrada. Revisa el historial para ver diferencias.')
            return redirect('home')
        
        return redirect('gestionar_caja')

    return render(request, 'finanzas/gestionar_caja.html', {
        'caja': caja_abierta
    })