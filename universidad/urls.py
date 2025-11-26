from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# Interceptar el login del admin: redirigir GET a raíz, pero permitir POST para errores
def admin_login_handler(request):
    if request.method == 'GET':
        # Redirigir GET a la raíz para mostrar la pantalla unificada
        next_url = request.GET.get('next', '/admin/')
        return redirect(f'/?next={next_url}')
    # Para POST, usar la vista normal del admin (manejará errores y mostrará admin/login.html)
    from django.contrib.admin.sites import site
    return site.login(request)

urlpatterns = [
    path('admin/login/', admin_login_handler, name='admin:login'),
    path('admin/', admin.site.urls),
    path('', include('gestion.urls')),
]


