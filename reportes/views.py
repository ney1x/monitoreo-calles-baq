from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ReporteForm
from .models import Reporte


@login_required
def crear_reporte(request):
    if request.method == 'POST':
        form = ReporteForm(request.POST, request.FILES)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.usuario = request.user
            reporte.save()
            return redirect('reporte_exitoso')
    else:
        form = ReporteForm()
    return render(request, 'reportes/crear_reporte.html', {'form': form})


def reporte_exitoso(request):
    return render(request, 'reportes/reporte_exitoso.html')


@login_required
def mis_reportes(request):
    reportes = Reporte.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'reportes/mis_reportes.html', {'reportes': reportes})
