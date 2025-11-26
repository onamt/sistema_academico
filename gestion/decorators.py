from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """Decorador que requiere que el usuario sea admin (autenticado en Django admin)"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, 'Acceso denegado. Se requiere permisos de administrador.')
            return redirect('admin:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def estudiante_required(view_func):
    """Decorador que requiere que el usuario sea un estudiante autenticado"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        estudiante_id = request.session.get('estudiante_id')
        if not estudiante_id:
            messages.error(request, 'Debes iniciar sesión como estudiante para acceder a esta página.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def estudiante_owner_required(view_func):
    """Decorador que requiere que el estudiante autenticado sea el dueño del recurso"""
    @wraps(view_func)
    def _wrapped_view(request, pk, *args, **kwargs):
        estudiante_id = request.session.get('estudiante_id')
        if not estudiante_id:
            messages.error(request, 'Debes iniciar sesión como estudiante.')
            return redirect('dashboard')
        if estudiante_id != pk:
            messages.error(request, 'No tienes permiso para acceder a esta información.')
            return redirect('notas_estudiante', pk=estudiante_id)
        return view_func(request, pk, *args, **kwargs)
    return _wrapped_view

