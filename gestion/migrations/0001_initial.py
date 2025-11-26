from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Asignatura',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=10, unique=True)),
                ('nombre', models.CharField(max_length=100)),
                ('creditos', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(30)])),
                ('profesor', models.CharField(max_length=100)),
            ],
            options={'ordering': ['codigo']},
        ),
        migrations.CreateModel(
            name='Estudiante',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('apellido', models.CharField(max_length=100)),
                ('matricula', models.CharField(max_length=20, unique=True)),
                ('carrera', models.CharField(max_length=100)),
                ('correo', models.EmailField(max_length=254, unique=True)),
            ],
            options={'ordering': ['apellido', 'nombre']},
        ),
        migrations.CreateModel(
            name='Horario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia', models.CharField(choices=[('LUN', 'Lunes'), ('MAR', 'Martes'), ('MIE', 'Miércoles'), ('JUE', 'Jueves'), ('VIE', 'Viernes'), ('SAB', 'Sábado')], max_length=3)),
                ('hora', models.TimeField()),
                ('aula', models.CharField(max_length=50)),
                ('asignatura', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='horarios', to='gestion.asignatura')),
            ],
            options={'ordering': ['dia', 'hora'], 'verbose_name_plural': 'Horarios'},
        ),
        migrations.CreateModel(
            name='Calificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('asignatura', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calificaciones', to='gestion.asignatura')),
                ('estudiante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calificaciones', to='gestion.estudiante')),
            ],
            options={'verbose_name_plural': 'Calificaciones'},
        ),
        migrations.AlterUniqueTogether(name='calificacion', unique_together={('estudiante', 'asignatura')}),
    ]


