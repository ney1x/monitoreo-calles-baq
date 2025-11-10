from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.usuarios.models import Rol
from apps.reportes.models import PrioridadReporte, EstadoReporte

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Poblar base de datos con datos iniciales del sistema'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🔄 Poblando base de datos...'))

        # ============================================
        # 1. CREAR ROLES
        # ============================================
        self.stdout.write('\n📋 Creando roles...')
        roles_data = [
            {'nombre': 'Ciudadano', 'descripcion': 'Usuario ciudadano que reporta incidencias'},
            {'nombre': 'Técnico', 'descripcion': 'Técnico de mantenimiento vial'},
            {'nombre': 'Autoridad', 'descripcion': 'Autoridad municipal supervisora'},
            {'nombre': 'Administrador', 'descripcion': 'Administrador del sistema'},
        ]

        roles = {}
        for rol_data in roles_data:
            rol, created = Rol.objects.get_or_create(
                nombre=rol_data['nombre'],
                defaults={'descripcion': rol_data['descripcion']}
            )
            roles[rol.nombre] = rol
            status = '✅ Creado' if created else '⚠️  Ya existía'
            self.stdout.write(f'  {status}: {rol.nombre}')

        # ============================================
        # 2. CREAR PRIORIDADES
        # ============================================
        self.stdout.write('\n🔴 Creando prioridades...')
        prioridades_data = [
            ('Baja', 1),
            ('Media', 2),
            ('Alta', 3),
            ('Crítica', 4),
        ]

        for nombre, nivel in prioridades_data:
            prioridad, created = PrioridadReporte.objects.get_or_create(
                nombre=nombre,
                defaults={'nivel_gravedad': nivel}
            )
            status = '✅ Creado' if created else '⚠️  Ya existía'
            self.stdout.write(f'  {status}: {nombre} (Nivel {nivel})')

        # ============================================
        # 3. CREAR ESTADOS
        # ============================================
        self.stdout.write('\n📊 Creando estados...')
        estados_data = [
            ('Nuevo', 'Reporte recién creado, pendiente de revisión'),
            ('En Revisión', 'Reporte siendo revisado por autoridades'),
            ('Asignado', 'Reporte asignado a un técnico'),
            ('En Proceso', 'Técnico trabajando en la reparación'),
            ('Resuelto', 'Problema solucionado'),
            ('Rechazado', 'Reporte rechazado o inválido'),
        ]

        for nombre, descripcion in estados_data:
            estado, created = EstadoReporte.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': descripcion}
            )
            status = '✅ Creado' if created else '⚠️  Ya existía'
            self.stdout.write(f'  {status}: {nombre}')

        # ============================================
        # 4. CREAR USUARIOS DE PRUEBA
        # ============================================
        self.stdout.write('\n👥 Creando usuarios de prueba...')
        
        usuarios_data = [
            {
                'username': 'ciudadano1',
                'email': 'ciudadano@test.com',
                'password': 'ciudadano123',
                'rol': roles['Ciudadano'],
                'telefono': '3001234567',
            },
            {
                'username': 'tecnico1',
                'email': 'tecnico@test.com',
                'password': 'tecnico123',
                'rol': roles['Técnico'],
                'telefono': '3002345678',
            },
            {
                'username': 'autoridad1',
                'email': 'autoridad@test.com',
                'password': 'autoridad123',
                'rol': roles['Autoridad'],
                'telefono': '3003456789',
            },
        ]

        for user_data in usuarios_data:
            if not Usuario.objects.filter(username=user_data['username']).exists():
                usuario = Usuario.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                )
                usuario.rol = user_data['rol']
                usuario.telefono = user_data['telefono']
                usuario.save()
                self.stdout.write(f'  ✅ Creado: {usuario.username} ({usuario.rol.nombre})')
            else:
                self.stdout.write(f'  ⚠️  Ya existía: {user_data["username"]}')

        # ============================================
        # 5. CREAR REPORTE DE EJEMPLO
        # ============================================
        self.stdout.write('\n📝 Creando reporte de ejemplo...')
        from apps.reportes.models import Reporte
        
        ciudadano = Usuario.objects.get(username='ciudadano1')
        estado_nuevo = EstadoReporte.objects.get(nombre='Nuevo')
        prioridad_alta = PrioridadReporte.objects.get(nombre='Alta')

        if not Reporte.objects.filter(titulo='Bache en Calle 72').exists():
            reporte = Reporte.objects.create(
                usuario=ciudadano,
                titulo='Bache en Calle 72',
                tipo='bache',
                descripcion='Bache de gran tamaño que afecta el tráfico vehicular',
                latitud=10.9878,
                longitud=-74.7889,
                direccion='Calle 72 #43-85, Barranquilla',
                estado=estado_nuevo,
                prioridad=prioridad_alta,
            )
            self.stdout.write(f'  ✅ Reporte creado: #{reporte.id}')
        else:
            self.stdout.write('  ⚠️  Reporte de ejemplo ya existe')

        # ============================================
        # RESUMEN FINAL
        # ============================================
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('✅ Base de datos poblada exitosamente!'))
        self.stdout.write('='*50)
        self.stdout.write('\n📊 Resumen:')
        self.stdout.write(f'  • Roles: {Rol.objects.count()}')
        self.stdout.write(f'  • Prioridades: {PrioridadReporte.objects.count()}')
        self.stdout.write(f'  • Estados: {EstadoReporte.objects.count()}')
        self.stdout.write(f'  • Usuarios: {Usuario.objects.count()}')
        self.stdout.write(f'  • Reportes: {Reporte.objects.count()}')
        
        self.stdout.write('\n🔐 Usuarios de prueba:')
        self.stdout.write('  • ciudadano1 / ciudadano123')
        self.stdout.write('  • tecnico1 / tecnico123')
        self.stdout.write('  • autoridad1 / autoridad123')
        self.stdout.write('\n')
