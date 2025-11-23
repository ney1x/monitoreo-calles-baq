from django import forms
from .models import Reporte, Evidencia


class ReporteForm(forms.ModelForm):
    """Formulario para crear reportes con geolocalización"""
    
    # Campos ocultos para coordenadas GPS (se llenan con JavaScript)
    # OPCIONALES hasta que se implemente GPS completo
    latitud = forms.DecimalField(
        widget=forms.HiddenInput(),
        required=False
    )
    longitud = forms.DecimalField(
        widget=forms.HiddenInput(),
        required=False
    )
    
    # Campo adicional para evidencia (foto/video)
    evidencia = forms.FileField(
        required=False,
        label='Foto o Video (opcional)',
        help_text='Sube una foto o video del incidente',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,video/*'
        })
    )

    class Meta:
        model = Reporte
        fields = ['tipo', 'titulo', 'descripcion', 'latitud', 'longitud', 'direccion']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-control',
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Bache profundo en vía principal'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe detalladamente el problema...'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Calle 72 #43-85, Barranquilla'
            }),
        }
        labels = {
            'tipo': 'Tipo de falla',
            'titulo': 'Título del reporte',
            'descripcion': 'Descripción',
            'direccion': 'Dirección',
        }


class EvidenciaForm(forms.ModelForm):
    """Formulario para subir evidencias (fotos/videos)"""
    
    class Meta:
        model = Evidencia
        fields = ['tipo_evidencia', 'archivo']
        widgets = {
            'tipo_evidencia': forms.Select(attrs={
                'class': 'form-control'
            }),
            'archivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,video/*'
            }),
        }

