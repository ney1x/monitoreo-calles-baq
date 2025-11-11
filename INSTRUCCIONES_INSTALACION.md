# 📋 INSTRUCCIONES DE INSTALACIÓN

## Requisitos Previos
- Python 3.12 o superior
- pip (gestor de paquetes de Python)

## Pasos de Instalación

### 1. Clonar/Descomprimir el proyecto
```bash
cd monitoreo_calles
```

### 2. Crear entorno virtual (opcional pero recomendado)
```bash
python -m venv venv
```

**Activar entorno virtual:**
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

### 3. Instalar dependencias
```bash
pip install django==5.2.7 pillow
```

### 4. Crear base de datos y aplicar migraciones
```bash
python manage.py migrate
```

### 5. Cargar datos iniciales (usuarios de prueba, reportes, etc.)
```bash
python manage.py loaddata datos_iniciales.json
```

### 6. Ejecutar el servidor
```bash
python manage.py runserver
```

### 7. Acceder al sistema
Abre tu navegador en: **http://127.0.0.1:8000/**

---

## 👥 Usuarios de Prueba

### Administrador
- Usuario: `admin`
- Contraseña: `admin123`

### Ciudadano
- Usuario: `ciudadano1`
- Contraseña: `ciudadano123`

### Técnico
- Usuario: `tecnico1`
- Contraseña: `tecnico123`

### Autoridad
- Usuario: `autoridad1`
- Contraseña: `autoridad123`

---

## 🔧 Comandos Útiles

### Crear superusuario (si necesitas uno nuevo)
```bash
python manage.py createsuperuser
```

### Acceder al panel de administración
http://127.0.0.1:8000/admin/

### Poblar datos adicionales (opcional)
```bash
python manage.py poblar_datos
```

---

## ⚠️ Solución de Problemas

### Error: "No module named 'django'"
```bash
pip install django==5.2.7
```

### Error: "no such table"
```bash
python manage.py migrate
python manage.py loaddata datos_iniciales.json
```

### Error: "Port already in use"
```bash
python manage.py runserver 8001
```
(Cambia el puerto a 8001, 8002, etc.)

---

## 📁 Estructura del Proyecto

```
monitoreo_calles/
├── manage.py
├── db.sqlite3 (se crea automáticamente)
├── datos_iniciales.json (datos de prueba)
├── apps/
│   ├── usuarios/ (gestión de usuarios y roles)
│   ├── reportes/ (reportes de calles)
│   └── core/ (datos base del sistema)
├── templates/ (plantillas HTML)
├── static/ (CSS, JS, imágenes)
└── media/ (archivos subidos por usuarios)
```

---

## 🚀 Tecnologías Utilizadas

- **Backend**: Django 5.2.7
- **Frontend**: Bootstrap 5.3.0
- **Base de Datos**: SQLite
- **Mapas**: Leaflet 1.9.4

---

## 📞 Soporte

Si tienes problemas durante la instalación, verifica:
1. ✅ Python 3.12+ instalado
2. ✅ Todas las dependencias instaladas
3. ✅ Migraciones aplicadas
4. ✅ Datos iniciales cargados
