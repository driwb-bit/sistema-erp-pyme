from django import forms
from django.forms import inlineformset_factory
from .models import Venta, DetalleVenta

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente'] # El usuario lo ponemos automático en la vista
        widgets = {
            'cliente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Cliente'}),
        }

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

# Esto es la magia: Crea una "fábrica" de formularios hijos vinculados al padre
DetalleVentaFormSet = inlineformset_factory(
    Venta, 
    DetalleVenta, 
    form=DetalleVentaForm,
    extra=1,       # Muestra 1 fila vacía por defecto
    can_delete=True # Permite borrar filas
)