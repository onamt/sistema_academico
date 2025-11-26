from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('gestion', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='estudiante',
            name='clave',
            field=models.CharField(blank=True, default='', max_length=128),
        ),
    ]


