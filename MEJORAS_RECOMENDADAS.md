# Mejoras Recomendadas - Sistema de Gestión Académica

## 🔒 1. SEGURIDAD Y AUTENTICACIÓN

### Rate Limiting en Login
```python
# En views.py - notas_login
from django.core.cache import cache
from django.http import HttpResponseForbidden

def notas_login(request):
    # Limitar intentos de login
    ip = request.META.get('REMOTE_ADDR')
    cache_key = f'login_attempts_{ip}'
    attempts = cache.get(cache_key, 0)
    
    if attempts >= 5:
        messages.error(request, 'Demasiados intentos fallidos. Intenta más tarde.')
        return redirect('dashboard')
    
    # ... resto del código ...
    
    if not form.is_valid():
        cache.set(cache_key, attempts + 1, 300)  # 5 minutos
        messages.error(request, 'Matrícula o contraseña inválidas.')
        return redirect('dashboard')
    
    cache.delete(cache_key)  # Limpiar al éxito
```

### Timeout de Sesión
```python
# En settings.py
SESSION_COOKIE_AGE = 3600  # 1 hora para estudiantes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```

### Validación de Contraseña Mejorada
```python
# En forms.py - CambiarClaveForm
import re

def clean_nueva1(self):
    nueva1 = self.cleaned_data.get('nueva1')
    if nueva1:
        if len(nueva1) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')
        if not re.search(r'[A-Z]', nueva1):
            raise forms.ValidationError('La contraseña debe contener al menos una mayúscula.')
        if not re.search(r'[0-9]', nueva1):
            raise forms.ValidationError('La contraseña debe contener al menos un número.')
    return nueva1
```

---

## 📊 2. VALIDACIONES DE NEGOCIO

### Modelo de Inscripción
```python
# En models.py
class Inscripcion(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('estudiante', 'asignatura')
        verbose_name_plural = 'Inscripciones'
    
    def __str__(self):
        return f"{self.estudiante} - {self.asignatura}"
```

### Validar Inscripción antes de Calificar
```python
# En admin.py o forms.py
def clean(self):
    cleaned = super().clean()
    estudiante = cleaned.get('estudiante')
    asignatura = cleaned.get('asignatura')
    
    if estudiante and asignatura:
        inscripcion = Inscripcion.objects.filter(
            estudiante=estudiante,
            asignatura=asignatura,
            activa=True
        ).exists()
        
        if not inscripcion:
            raise forms.ValidationError(
                f'El estudiante {estudiante} no está inscrito en {asignatura}.'
            )
    
    return cleaned
```

---

## 🚀 3. FUNCIONALIDADES FALTANTES

### Búsqueda y Filtros en Listas
```python
# En views.py - estudiantes_list
def estudiantes_list(request):
    query = request.GET.get('q', '')
    carrera = request.GET.get('carrera', '')
    
    estudiantes = Estudiante.objects.all()
    
    if query:
        estudiantes = estudiantes.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(matricula__icontains=query)
        )
    
    if carrera:
        estudiantes = estudiantes.filter(carrera=carrera)
    
    # Paginación
    from django.core.paginator import Paginator
    paginator = Paginator(estudiantes, 20)
    page = request.GET.get('page')
    estudiantes = paginator.get_page(page)
    
    return render(request, 'estudiantes_list.html', {
        'estudiantes': estudiantes,
        'query': query,
        'carrera': carrera,
    })
```

### Dashboard Administrativo Mejorado
```python
# Nueva vista admin_dashboard
@admin_required
def admin_dashboard(request):
    total_estudiantes = Estudiante.objects.count()
    total_asignaturas = Asignatura.objects.count()
    total_calificaciones = Calificacion.objects.count()
    
    # Estudiantes por carrera
    estudiantes_por_carrera = Estudiante.objects.values('carrera').annotate(
        total=Count('id')
    ).order_by('-total')
    
    # Top estudiantes
    top_estudiantes = Estudiante.objects.annotate(
        promedio=Avg('calificaciones__nota')
    ).filter(promedio__isnull=False).order_by('-promedio')[:10]
    
    # Asignaturas más calificadas
    asignaturas_populares = Asignatura.objects.annotate(
        total_calificaciones=Count('calificaciones')
    ).order_by('-total_calificaciones')[:5]
    
    return render(request, 'admin_dashboard.html', {
        'total_estudiantes': total_estudiantes,
        'total_asignaturas': total_asignaturas,
        'total_calificaciones': total_calificaciones,
        'estudiantes_por_carrera': estudiantes_por_carrera,
        'top_estudiantes': top_estudiantes,
        'asignaturas_populares': asignaturas_populares,
    })
```

### Vista Mejorada para Estudiantes
```python
@estudiante_owner_required
def notas_estudiante(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    
    # Calificaciones
    calificaciones = Calificacion.objects.filter(
        estudiante=estudiante
    ).select_related('asignatura').order_by('asignatura__codigo')
    
    # Asignaturas inscritas (si existe modelo Inscripcion)
    # asignaturas_inscritas = Inscripcion.objects.filter(
    #     estudiante=estudiante, activa=True
    # ).select_related('asignatura')
    
    # Horarios (si el estudiante está inscrito)
    # horarios = Horario.objects.filter(
    #     asignatura__inscripciones__estudiante=estudiante,
    #     asignatura__inscripciones__activa=True
    # ).select_related('asignatura')
    
    promedio = calificaciones.aggregate(prom=Avg('nota'))['prom']
    
    # Estadísticas adicionales
    total_asignaturas = calificaciones.count()
    aprobadas = calificaciones.filter(nota__gte=60).count()
    reprobadas = total_asignaturas - aprobadas
    
    return render(request, 'notas_estudiante.html', {
        'estudiante': estudiante,
        'calificaciones': calificaciones,
        'promedio': promedio,
        'total_asignaturas': total_asignaturas,
        'aprobadas': aprobadas,
        'reprobadas': reprobadas,
        'cambiar_clave_form': CambiarClaveForm(estudiante),
    })
```

---

## ⚡ 4. OPTIMIZACIONES

### Índices en Modelos
```python
# En models.py
class Estudiante(models.Model):
    matricula = models.CharField(max_length=20, unique=True, db_index=True)
    correo = models.EmailField(unique=True, db_index=True)
    carrera = models.CharField(max_length=100, db_index=True)  # Para filtros

class Calificacion(models.Model):
    nota = models.DecimalField(..., db_index=True)  # Para búsquedas por rango
```

### Cache para Dashboard
```python
# En views.py
from django.core.cache import cache

def dashboard(request):
    cache_key = 'dashboard_stats'
    stats = cache.get(cache_key)
    
    if not stats:
        stats = {
            'total_estudiantes': Estudiante.objects.count(),
            'total_asignaturas': Asignatura.objects.count(),
            'promedio_calificaciones': Calificacion.objects.aggregate(
                promedio=Avg('nota')
            )['promedio'],
        }
        cache.set(cache_key, stats, 300)  # Cache por 5 minutos
    
    # ... resto del código ...
```

---

## 🛡️ 5. MANEJO DE ERRORES

### Try-Except en Operaciones Críticas
```python
@admin_required
def estudiantes_delete(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    if request.method == 'POST':
        try:
            # Verificar si tiene calificaciones
            if estudiante.calificaciones.exists():
                messages.warning(
                    request,
                    'No se puede eliminar el estudiante porque tiene calificaciones. '
                    'Primero elimina las calificaciones asociadas.'
                )
                return redirect('estudiantes_list')
            
            estudiante.delete()
            messages.success(request, 'Estudiante eliminado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar: {str(e)}')
            # Log del error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error eliminando estudiante {pk}: {str(e)}')
        
        return redirect('estudiantes_list')
    
    return render(request, 'confirm_delete.html', {
        'obj': estudiante,
        'back_url': reverse('estudiantes_list')
    })
```

---

## 📱 6. EXPERIENCIA DE USUARIO

### Mensajes de Error Más Descriptivos
```python
# En forms.py
class ConsultaNotasForm(forms.Form):
    def clean(self):
        cleaned = super().clean()
        matricula = cleaned.get('matricula')
        clave = cleaned.get('clave')
        
        if matricula and clave:
            try:
                estudiante = Estudiante.objects.get(matricula=matricula)
            except Estudiante.DoesNotExist:
                raise forms.ValidationError(
                    'No existe un estudiante con esa matrícula. '
                    'Verifica que la matrícula sea correcta.'
                )
            
            if not estudiante.clave:
                raise forms.ValidationError(
                    'Este estudiante no tiene contraseña asignada. '
                    'Contacta al administrador.'
                )
            
            if not estudiante.check_clave(clave):
                raise forms.ValidationError(
                    'Contraseña incorrecta. Si olvidaste tu contraseña, '
                    'contacta al administrador.'
                )
            
            cleaned['estudiante'] = estudiante
        
        return cleaned
```

---

## 📋 RESUMEN DE PRIORIDADES

### 🔴 ALTA PRIORIDAD
1. Rate limiting en login
2. Modelo de Inscripción
3. Validar inscripción antes de calificar
4. Búsqueda y filtros en listas
5. Paginación
6. Manejo de errores con try-except

### 🟡 MEDIA PRIORIDAD
7. Dashboard administrativo mejorado
8. Timeout de sesión
9. Validación de contraseña mejorada
10. Cache para métricas
11. Índices en modelos

### 🟢 BAJA PRIORIDAD
12. Exportación de datos
13. Notificaciones
14. Historial de cambios
15. Gráficos y visualizaciones

