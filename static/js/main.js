// ============================================
// GEOLOCALIZACIÓN
// ============================================

/**
 * Obtiene la ubicación actual del usuario mediante GPS
 */
function obtenerUbicacion() {
    const btnUbicacion = document.getElementById('btnObtenerUbicacion');
    const statusDiv = document.getElementById('locationStatus');
    const latInput = document.getElementById('id_latitud');
    const lngInput = document.getElementById('id_longitud');
    const direccionInput = document.getElementById('id_direccion');
    
    if (!navigator.geolocation) {
        mostrarEstadoUbicacion('error', 'Tu navegador no soporta geolocalización');
        return;
    }
    
    // Mostrar estado de carga
    mostrarEstadoUbicacion('loading', 'Obteniendo tu ubicación...');
    btnUbicacion.disabled = true;
    btnUbicacion.innerHTML = '<i class="bi bi-hourglass-split"></i> Obteniendo...';
    
    navigator.geolocation.getCurrentPosition(
        // Éxito
        function(position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            
            latInput.value = lat;
            lngInput.value = lng;
            
            // Obtener dirección usando Nominatim (OpenStreetMap)
            obtenerDireccion(lat, lng, direccionInput);
            
            mostrarEstadoUbicacion('success', 
                `✓ Ubicación obtenida: ${lat.toFixed(6)}, ${lng.toFixed(6)}`);
            
            btnUbicacion.disabled = false;
            btnUbicacion.innerHTML = '<i class="bi bi-geo-alt-fill"></i> Ubicación Obtenida';
            btnUbicacion.classList.remove('btn-primary');
            btnUbicacion.classList.add('btn-success');
            
            // Si hay un mapa, centrarlo en la ubicación
            if (typeof mostrarEnMapa === 'function') {
                mostrarEnMapa(lat, lng);
            }
        },
        // Error
        function(error) {
            let mensaje = 'Error al obtener ubicación';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    mensaje = 'Permiso de ubicación denegado. Por favor, habilita el GPS.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    mensaje = 'Información de ubicación no disponible.';
                    break;
                case error.TIMEOUT:
                    mensaje = 'Tiempo de espera agotado.';
                    break;
            }
            
            mostrarEstadoUbicacion('error', mensaje);
            btnUbicacion.disabled = false;
            btnUbicacion.innerHTML = '<i class="bi bi-geo-alt"></i> Reintentar';
        },
        // Opciones
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

/**
 * Obtiene la dirección a partir de coordenadas usando Nominatim
 */
function obtenerDireccion(lat, lng, inputElement) {
    const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&addressdetails=1`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.display_name) {
                inputElement.value = data.display_name;
            }
        })
        .catch(error => {
            console.error('Error al obtener dirección:', error);
            inputElement.value = `Lat: ${lat.toFixed(6)}, Lng: ${lng.toFixed(6)}`;
        });
}

/**
 * Muestra el estado de la obtención de ubicación
 */
function mostrarEstadoUbicacion(tipo, mensaje) {
    const statusDiv = document.getElementById('locationStatus');
    if (!statusDiv) return;
    
    statusDiv.className = `location-status ${tipo}`;
    statusDiv.innerHTML = `<i class="bi bi-${getIconoEstado(tipo)}"></i> ${mensaje}`;
    statusDiv.style.display = 'block';
}

function getIconoEstado(tipo) {
    switch(tipo) {
        case 'loading': return 'hourglass-split';
        case 'success': return 'check-circle-fill';
        case 'error': return 'exclamation-triangle-fill';
        default: return 'info-circle-fill';
    }
}

// ============================================
// UPLOAD DE ARCHIVOS CON PREVIEW
// ============================================

/**
 * Maneja la vista previa de archivos (imágenes y videos)
 */
function setupFileUpload() {
    const fileInput = document.getElementById('id_archivo');
    const previewContainer = document.getElementById('previewContainer');
    
    if (!fileInput || !previewContainer) return;
    
    // Almacena los archivos seleccionados
    let archivosSeleccionados = [];
    
    fileInput.addEventListener('change', function(e) {
        const archivos = Array.from(e.target.files);
        
        archivos.forEach(archivo => {
            // Validar tipo
            if (!validarTipoArchivo(archivo)) {
                alert(`El archivo ${archivo.name} no es válido. Solo se permiten imágenes y videos.`);
                return;
            }
            
            // Validar tamaño (50MB max)
            if (archivo.size > 50 * 1024 * 1024) {
                alert(`El archivo ${archivo.name} es demasiado grande. Máximo 50MB.`);
                return;
            }
            
            archivosSeleccionados.push(archivo);
            mostrarPreview(archivo, previewContainer);
        });
    });
}

function validarTipoArchivo(archivo) {
    const tiposValidos = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'video/mp4', 'video/mpeg', 'video/quicktime'];
    return tiposValidos.includes(archivo.type);
}

function mostrarPreview(archivo, container) {
    const reader = new FileReader();
    
    reader.onload = function(e) {
        const previewItem = document.createElement('div');
        previewItem.className = 'preview-item fade-in';
        
        let elemento;
        if (archivo.type.startsWith('image/')) {
            elemento = `<img src="${e.target.result}" alt="Preview">`;
        } else if (archivo.type.startsWith('video/')) {
            elemento = `<video src="${e.target.result}" controls></video>`;
        }
        
        previewItem.innerHTML = `
            ${elemento}
            <button type="button" class="remove-btn" onclick="eliminarPreview(this)">
                <i class="bi bi-x"></i>
            </button>
        `;
        
        container.appendChild(previewItem);
    };
    
    reader.readAsDataURL(archivo);
}

function eliminarPreview(btn) {
    btn.closest('.preview-item').remove();
}

// ============================================
// VALIDACIÓN DE FORMULARIOS
// ============================================

/**
 * Valida formulario antes de enviar
 */
function validarFormularioReporte() {
    const form = document.getElementById('formReporte');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        const latitud = document.getElementById('id_latitud').value;
        const longitud = document.getElementById('id_longitud').value;
        
        if (!latitud || !longitud) {
            e.preventDefault();
            alert('Por favor, obtén tu ubicación antes de enviar el reporte.');
            document.getElementById('btnObtenerUbicacion').focus();
            return false;
        }
    });
}

// ============================================
// CONFIRMACIONES
// ============================================

/**
 * Confirma acciones críticas
 */
function confirmarAccion(mensaje) {
    return confirm(mensaje || '¿Estás seguro de realizar esta acción?');
}

// ============================================
// AUTO-DISMISS DE ALERTAS
// ============================================

function autoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// ============================================
// FILTROS Y BÚSQUEDA
// ============================================

/**
 * Filtrado en tiempo real de elementos
 */
function setupFiltros() {
    const searchInput = document.getElementById('searchInput');
    const estadoFilter = document.getElementById('estadoFilter');
    const prioridadFilter = document.getElementById('prioridadFilter');
    
    if (searchInput) {
        searchInput.addEventListener('input', aplicarFiltros);
    }
    
    if (estadoFilter) {
        estadoFilter.addEventListener('change', aplicarFiltros);
    }
    
    if (prioridadFilter) {
        prioridadFilter.addEventListener('change', aplicarFiltros);
    }
}

function aplicarFiltros() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const estadoSeleccionado = document.getElementById('estadoFilter')?.value || '';
    const prioridadSeleccionada = document.getElementById('prioridadFilter')?.value || '';
    
    const items = document.querySelectorAll('.reporte-item');
    
    items.forEach(item => {
        const texto = item.textContent.toLowerCase();
        const estado = item.dataset.estado || '';
        const prioridad = item.dataset.prioridad || '';
        
        const coincideTexto = texto.includes(searchTerm);
        const coincideEstado = !estadoSeleccionado || estado === estadoSeleccionado;
        const coincidePrioridad = !prioridadSeleccionada || prioridad === prioridadSeleccionada;
        
        if (coincideTexto && coincideEstado && coincidePrioridad) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

// ============================================
// INICIALIZACIÓN AL CARGAR LA PÁGINA
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss de alertas
    autoDismissAlerts();
    
    // Setup de upload de archivos
    setupFileUpload();
    
    // Validación de formularios
    validarFormularioReporte();
    
    // Setup de filtros
    setupFiltros();
    
    // Tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Popovers de Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// ============================================
// UTILIDADES
// ============================================

/**
 * Formatea fecha a español
 */
function formatearFecha(fecha) {
    const opciones = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(fecha).toLocaleDateString('es-CO', opciones);
}

/**
 * Copia texto al portapapeles
 */
function copiarAlPortapapeles(texto) {
    navigator.clipboard.writeText(texto).then(() => {
        alert('Copiado al portapapeles');
    });
}
