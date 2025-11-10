from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Rol, Usuario


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'telefono',
        'get_rol',
        'activo',
        'is_staff',
        'creadoEn',
    )
    
    list_filter = ('rol', 'activo', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'telefono')
        }),
        ('Rol y Estado', {
            'fields': ('rol', 'activo')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas', {
            'fields': ('creadoEn', 'ultimoInicioSesion', 'last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'telefono',
                'password1',
                'password2',
                'rol',
                'activo',
            ),
        }),
    )

    readonly_fields = ('creadoEn', 'ultimoInicioSesion', 'last_login', 'date_joined')

    def get_rol(self, obj):
        return obj.rol.nombre if obj.rol else '-'
    get_rol.short_description = 'Rol'
