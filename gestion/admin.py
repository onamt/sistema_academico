from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Estudiante, Asignatura, Calificacion, Horario


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ("matricula", "apellido", "nombre", "carrera", "correo")
    search_fields = ("matricula", "nombre", "apellido", "correo", "carrera")

    def save_model(self, request, obj, form, change):
        # Si se edita la clave y no parece hasheada, la hasheamos automáticamente.
        if obj.clave and not obj.clave.startswith(('pbkdf2_', 'argon2$', 'bcrypt$', 'scrypt$')):
            obj.clave = make_password(obj.clave)
        super().save_model(request, obj, form, change)


@admin.register(Asignatura)
class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "creditos", "profesor")
    search_fields = ("codigo", "nombre", "profesor")


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ("estudiante", "asignatura", "nota")
    search_fields = ("estudiante__nombre", "estudiante__apellido", "asignatura__nombre", "asignatura__codigo")


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ("asignatura", "dia", "hora", "aula")
    list_filter = ("dia",)


