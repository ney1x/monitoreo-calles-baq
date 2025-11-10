from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario, Rol

class RegistroForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'telefono']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        # Obtener el rol de ciudadano desde la base de datos
        rol_ciudadano = Rol.objects.get(nombre='Ciudadano')
        user.rol = rol_ciudadano
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    pass
