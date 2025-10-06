from django import forms
from .models import Reporte

class ReporteForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = ['tipo', 'descripcion', 'direccion', 'foto', 'video']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe el problema...'}),
            'direccion': forms.TextInput(attrs={'placeholder': 'Ejemplo: Calle 72 #43-85, Barranquilla'}),
        }

