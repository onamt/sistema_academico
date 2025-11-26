from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import MinValueValidator, MaxValueValidator


class Estudiante(models.Model):
    nombre = models.CharField(max_length=100, db_index=True)
    apellido = models.CharField(max_length=100, db_index=True)
    matricula = models.CharField(max_length=20, unique=True, db_index=True)
    carrera = models.CharField(max_length=100, db_index=True)
    correo = models.EmailField(unique=True, db_index=True)
    # Almacena la contraseña hasheada
    clave = models.CharField(max_length=128, blank=True, default="")

    class Meta:
        ordering = ['apellido', 'nombre']

    def __str__(self) -> str:
        return f"{self.nombre} {self.apellido} ({self.matricula})"

    # Helpers de contraseña
    def set_clave(self, raw_password: str) -> None:
        self.clave = make_password(raw_password)

    def check_clave(self, raw_password: str) -> bool:
        if not self.clave:
            return False
        return check_password(raw_password, self.clave)


class Asignatura(models.Model):
    codigo = models.CharField(max_length=10, unique=True, db_index=True)
    nombre = models.CharField(max_length=100, db_index=True)
    creditos = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)])
    profesor = models.CharField(max_length=100, db_index=True)

    class Meta:
        ordering = ['codigo']

    def __str__(self) -> str:
        return f"{self.codigo} - {self.nombre}"


class Calificacion(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='calificaciones', db_index=True)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, related_name='calificaciones', db_index=True)
    nota = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], db_index=True)

    class Meta:
        unique_together = ('estudiante', 'asignatura')
        verbose_name_plural = 'Calificaciones'

    def __str__(self) -> str:
        return f"{self.estudiante} - {self.asignatura}: {self.nota}"


class Horario(models.Model):
    DIAS = [
        ('LUN', 'Lunes'),
        ('MAR', 'Martes'),
        ('MIE', 'Miércoles'),
        ('JUE', 'Jueves'),
        ('VIE', 'Viernes'),
        ('SAB', 'Sábado'),
    ]

    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, related_name='horarios')
    dia = models.CharField(max_length=3, choices=DIAS)
    hora = models.TimeField()
    aula = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = 'Horarios'
        ordering = ['dia', 'hora']

    def __str__(self) -> str:
        return f"{self.get_dia_display()} {self.hora} - {self.asignatura} ({self.aula})"


