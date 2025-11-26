from django.test import TestCase
from .models import Estudiante


class EstudianteModelTest(TestCase):
    def test_crear_estudiante(self):
        estudiante = Estudiante.objects.create(
            nombre='Ana',
            apellido='Pérez',
            matricula='A001',
            carrera='Ingeniería',
            correo='ana.perez@example.com',
        )
        self.assertEqual(str(estudiante), 'Ana Pérez (A001)')
        self.assertEqual(Estudiante.objects.count(), 1)


