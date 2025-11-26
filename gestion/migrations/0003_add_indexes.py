from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ('gestion', '0002_estudiante_clave'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estudiante',
            name='nombre',
            field=models.CharField(db_index=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='estudiante',
            name='apellido',
            field=models.CharField(db_index=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='estudiante',
            name='matricula',
            field=models.CharField(db_index=True, max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='estudiante',
            name='carrera',
            field=models.CharField(db_index=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='estudiante',
            name='correo',
            field=models.EmailField(db_index=True, max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='asignatura',
            name='codigo',
            field=models.CharField(db_index=True, max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='asignatura',
            name='nombre',
            field=models.CharField(db_index=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='asignatura',
            name='profesor',
            field=models.CharField(db_index=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='calificacion',
            name='estudiante',
            field=models.ForeignKey(db_index=True, on_delete=models.deletion.CASCADE, related_name='calificaciones', to='gestion.estudiante'),
        ),
        migrations.AlterField(
            model_name='calificacion',
            name='asignatura',
            field=models.ForeignKey(db_index=True, on_delete=models.deletion.CASCADE, related_name='calificaciones', to='gestion.asignatura'),
        ),
        migrations.AlterField(
            model_name='calificacion',
            name='nota',
            field=models.DecimalField(db_index=True, decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
    ]

