from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):

    list_display = (
        'username',
        'email',
        'rol',
        'activo',
        'is_staff',
        'creadoEn',
        'ultimoInicioSesion',
    )

    list_filter = ('rol', 'activo', 'is_staff')

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Información personal', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Rol y permisos', {
            'fields': (
                'rol',
                'activo',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Fechas importantes', {
            'fields': (
                'creadoEn',
                'ultimoInicioSesion',
                'last_login',
                'date_joined',
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password1',
                'password2',
                'rol',
                'activo',
                'is_staff',
                'is_active',
            ),
        }),
    )

    readonly_fields = ('creadoEn', 'ultimoInicioSesion', 'last_login', 'date_joined')
