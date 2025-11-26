from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.cache import cache
from django.core.paginator import Paginator
import logging

from .models import Estudiante, Asignatura, Calificacion
from .forms import EstudianteForm, AsignaturaForm, ConsultaNotasForm, CambiarClaveForm
from .decorators import admin_required, estudiante_required, estudiante_owner_required

logger = logging.getLogger(__name__)


def dashboard(request):
    # Verificar si hay un estudiante logueado
    estudiante_id = request.session.get('estudiante_id')
    
    # Si es estudiante logueado, redirigir a sus notas
    if estudiante_id:
        return redirect('notas_estudiante', pk=estudiante_id)
    
    # Si es admin logueado, redirigir al panel de admin
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('/admin/')
    
    # Renderizar pantalla de login unificada
    from django.contrib.auth.forms import AuthenticationForm
    admin_form = AuthenticationForm(request)
    
    return render(
        request,
        'dashboard.html',
        {
            'consulta_form': ConsultaNotasForm(),
            'admin_form': admin_form,
            'next': request.GET.get('next', '/admin/'),
        },
    )


# Estudiantes CRUD
@admin_required
def estudiantes_list(request):
    estudiantes = Estudiante.objects.all()
    
    # Búsqueda
    query = request.GET.get('q', '').strip()
    if query:
        estudiantes = estudiantes.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(matricula__icontains=query) |
            Q(correo__icontains=query) |
            Q(carrera__icontains=query)
        )
    
    # Filtro por carrera
    carrera_filter = request.GET.get('carrera', '').strip()
    if carrera_filter:
        estudiantes = estudiantes.filter(carrera=carrera_filter)
    
    # Obtener lista de carreras únicas para el filtro
    carreras = Estudiante.objects.values_list('carrera', flat=True).distinct().order_by('carrera')
    
    # Paginación
    paginator = Paginator(estudiantes, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'estudiantes_list.html', {
        'estudiantes': page_obj,
        'query': query,
        'carrera_filter': carrera_filter,
        'carreras': carreras,
    })


@admin_required
def estudiantes_create(request):
    if request.method == 'POST':
        form = EstudianteForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                cache.delete('dashboard_stats')
                messages.success(request, 'Estudiante creado correctamente.')
                logger.info(f'Estudiante creado por {request.user.username}')
                return redirect('estudiantes_list')
            except Exception as e:
                logger.error(f'Error creando estudiante: {str(e)}', exc_info=True)
                messages.error(request, f'Error al crear el estudiante: {str(e)}')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = EstudianteForm()
    return render(request, 'estudiantes_form.html', {'form': form, 'is_create': True})


@admin_required
def estudiantes_update(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    if request.method == 'POST':
        form = EstudianteForm(request.POST, instance=estudiante)
        if form.is_valid():
            try:
                form.save()
                cache.delete('dashboard_stats')
                messages.success(request, 'Estudiante actualizado correctamente.')
                logger.info(f'Estudiante {pk} actualizado por {request.user.username}')
                return redirect('estudiantes_list')
            except Exception as e:
                logger.error(f'Error actualizando estudiante {pk}: {str(e)}', exc_info=True)
                messages.error(request, f'Error al actualizar el estudiante: {str(e)}')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = EstudianteForm(instance=estudiante)
    return render(request, 'estudiantes_form.html', {'form': form, 'is_create': False})


@admin_required
def estudiantes_delete(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    if request.method == 'POST':
        try:
            # Verificar si tiene calificaciones
            if estudiante.calificaciones.exists():
                messages.warning(
                    request,
                    f'No se puede eliminar el estudiante {estudiante} porque tiene calificaciones registradas. '
                    'Primero elimina las calificaciones asociadas desde el panel de administración.'
                )
                return redirect('estudiantes_list')
            
            estudiante.delete()
            # Invalidar cache del dashboard
            cache.delete('dashboard_stats')
            messages.success(request, 'Estudiante eliminado correctamente.')
            logger.info(f'Estudiante {pk} eliminado por {request.user.username}')
        except Exception as e:
            logger.error(f'Error eliminando estudiante {pk}: {str(e)}', exc_info=True)
            messages.error(request, f'Error al eliminar el estudiante: {str(e)}')
        return redirect('estudiantes_list')
    return render(request, 'confirm_delete.html', {'obj': estudiante, 'back_url': reverse('estudiantes_list')})


# Asignaturas CRUD
@admin_required
def asignaturas_list(request):
    asignaturas = Asignatura.objects.all()
    
    # Búsqueda
    query = request.GET.get('q', '').strip()
    if query:
        asignaturas = asignaturas.filter(
            Q(codigo__icontains=query) |
            Q(nombre__icontains=query) |
            Q(profesor__icontains=query)
        )
    
    # Paginación
    paginator = Paginator(asignaturas, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'asignaturas_list.html', {
        'asignaturas': page_obj,
        'query': query,
    })


@admin_required
def asignaturas_create(request):
    if request.method == 'POST':
        form = AsignaturaForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                cache.delete('dashboard_stats')
                messages.success(request, 'Asignatura creada correctamente.')
                return redirect('asignaturas_list')
            except Exception as e:
                logger.error(f'Error creando asignatura: {str(e)}', exc_info=True)
                messages.error(request, f'Error al crear la asignatura: {str(e)}')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = AsignaturaForm()
    return render(request, 'asignaturas_form.html', {'form': form, 'is_create': True})


@admin_required
def asignaturas_update(request, pk):
    asignatura = get_object_or_404(Asignatura, pk=pk)
    if request.method == 'POST':
        form = AsignaturaForm(request.POST, instance=asignatura)
        if form.is_valid():
            try:
                form.save()
                cache.delete('dashboard_stats')
                messages.success(request, 'Asignatura actualizada correctamente.')
                return redirect('asignaturas_list')
            except Exception as e:
                logger.error(f'Error actualizando asignatura {pk}: {str(e)}', exc_info=True)
                messages.error(request, f'Error al actualizar la asignatura: {str(e)}')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = AsignaturaForm(instance=asignatura)
    return render(request, 'asignaturas_form.html', {'form': form, 'is_create': False})


@admin_required
def asignaturas_delete(request, pk):
    asignatura = get_object_or_404(Asignatura, pk=pk)
    if request.method == 'POST':
        try:
            # Verificar si tiene calificaciones o horarios
            if asignatura.calificaciones.exists():
                messages.warning(
                    request,
                    f'No se puede eliminar la asignatura {asignatura} porque tiene calificaciones registradas. '
                    'Primero elimina las calificaciones asociadas.'
                )
                return redirect('asignaturas_list')
            
            asignatura.delete()
            cache.delete('dashboard_stats')
            messages.success(request, 'Asignatura eliminada correctamente.')
            logger.info(f'Asignatura {pk} eliminada por {request.user.username}')
        except Exception as e:
            logger.error(f'Error eliminando asignatura {pk}: {str(e)}', exc_info=True)
            messages.error(request, f'Error al eliminar la asignatura: {str(e)}')
        return redirect('asignaturas_list')
    return render(request, 'confirm_delete.html', {'obj': asignatura, 'back_url': reverse('asignaturas_list')})


# Consulta de notas de estudiante (login simple)
def notas_login(request):
    if request.method != 'POST':
        return redirect('dashboard')
    
    # Rate limiting: máximo 5 intentos por IP cada 5 minutos
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    cache_key = f'login_attempts_{ip}'
    attempts = cache.get(cache_key, 0)
    
    if attempts >= 5:
        messages.error(
            request,
            'Demasiados intentos fallidos. Por favor, intenta nuevamente en 5 minutos.'
        )
        logger.warning(f'Rate limit excedido para IP: {ip}')
        return redirect('dashboard')
    
    form = ConsultaNotasForm(request.POST)
    if form.is_valid():
        estudiante = form.cleaned_data['estudiante']
        # Limpiar intentos fallidos al éxito
        cache.delete(cache_key)
        # Crear sesión para el estudiante
        request.session['estudiante_id'] = estudiante.pk
        request.session['estudiante_nombre'] = f"{estudiante.nombre} {estudiante.apellido}"
        # Configurar timeout de sesión (1 hora)
        request.session.set_expiry(3600)
        messages.success(request, f'Bienvenido, {estudiante.nombre}!')
        logger.info(f'Estudiante {estudiante.pk} ({estudiante.matricula}) inició sesión desde IP: {ip}')
        return redirect('notas_estudiante', pk=estudiante.pk)
    
    # Incrementar intentos fallidos
    cache.set(cache_key, attempts + 1, 300)  # 5 minutos
    messages.error(request, 'Matrícula o contraseña inválidas.')
    logger.warning(f'Intento de login fallido desde IP: {ip}, intento: {attempts + 1}')
    return redirect('dashboard')


@estudiante_owner_required
def notas_estudiante(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    # Validación adicional: asegurar que el estudiante de la sesión coincide
    if request.session.get('estudiante_id') != pk:
        messages.error(request, 'No tienes permiso para acceder a esta información.')
        estudiante_id = request.session.get('estudiante_id')
        if estudiante_id:
            return redirect('notas_estudiante', pk=estudiante_id)
        return redirect('dashboard')
    
    # Solo mostrar las calificaciones del estudiante autenticado
    calificaciones = Calificacion.objects.filter(estudiante=estudiante).select_related('asignatura').order_by('asignatura__codigo')
    promedio = calificaciones.aggregate(prom=Avg('nota'))['prom']
    
    # Estadísticas adicionales
    total_asignaturas = calificaciones.count()
    aprobadas = calificaciones.filter(nota__gte=60).count() if total_asignaturas > 0 else 0
    reprobadas = total_asignaturas - aprobadas
    
    # Calcular créditos totales (suma de créditos de asignaturas calificadas)
    creditos_totales = sum(cal.asignatura.creditos for cal in calificaciones)
    
    return render(
        request,
        'notas_estudiante.html',
        {
            'estudiante': estudiante,
            'calificaciones': calificaciones,
            'promedio': promedio,
            'total_asignaturas': total_asignaturas,
            'aprobadas': aprobadas,
            'reprobadas': reprobadas,
            'creditos_totales': creditos_totales,
            'cambiar_clave_form': CambiarClaveForm(estudiante),
        },
    )


@estudiante_owner_required
def cambiar_clave(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    if request.method != 'POST':
        return redirect('notas_estudiante', pk=pk)
    
    form = CambiarClaveForm(estudiante, request.POST)
    if form.is_valid():
        try:
            nueva = form.cleaned_data['nueva1']
            estudiante.set_clave(nueva)
            estudiante.save(update_fields=['clave'])
            messages.success(request, 'Contraseña actualizada correctamente.')
            logger.info(f'Estudiante {pk} cambió su contraseña')
            return redirect('notas_estudiante', pk=pk)
        except Exception as e:
            logger.error(f'Error cambiando contraseña estudiante {pk}: {str(e)}', exc_info=True)
            messages.error(request, 'Error al actualizar la contraseña. Intenta nuevamente.')
    else:
        messages.error(request, 'Corrige los errores del formulario.')
    
    return redirect('notas_estudiante', pk=pk)


def notas_logout(request):
    """Cerrar sesión de estudiante"""
    estudiante_nombre = request.session.get('estudiante_nombre', 'Estudiante')
    request.session.flush()
    messages.success(request, f'Sesión cerrada. Hasta luego, {estudiante_nombre}!')
    return redirect('dashboard')


