# Generated by Django 5.1.9 on 2025-05-13 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Aulora_bakend', '0019_alter_itinerario_curso_fecha_agregado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itinerario_curso',
            name='fecha_agregado',
            field=models.DateField(),
        ),
    ]
