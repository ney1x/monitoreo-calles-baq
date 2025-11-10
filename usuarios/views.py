from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, LoginForm

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario registrado correctamente. Ahora puedes iniciar sesión.")
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)

                # REGISTRA LA FECHA DE INICIO DE SESIÓN
                user.registrar_inicio_sesion()

                messages.success(request, f"Bienvenido, {username}.")

                # REDIRECCIÓN CORRECTA SEGÚN ROLES DEL MODELO
                if user.rol == 'CIUDADANO':
                    return redirect('ciudadano_home')
                elif user.rol == 'TECNICO':
                    return redirect('tecnico_home')
                elif user.rol == 'AUTORIDAD':
                    return redirect('autoridad_home')
                elif user.rol == 'ADMIN':
                    return redirect('/admin/')  # Admin → Panel de administración

                return redirect('login')  # fallback
            else:
                messages.error(request, "Credenciales inválidas.")
        else:
            messages.error(request, "Error en el formulario.")
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect('login')


# Vistas por rol
@login_required
def ciudadano_home(request):
    return render(request, 'usuarios/ciudadano_home.html')

@login_required
def tecnico_home(request):
    return render(request, 'usuarios/tecnico_home.html')

@login_required
def autoridad_home(request):
    return render(request, 'usuarios/autoridad_home.html')