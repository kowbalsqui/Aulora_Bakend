# Generated by Django 5.1.9 on 2025-05-12 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Aulora_bakend', '0014_alter_itinerario_precio'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='cursos_completados',
            field=models.IntegerField(default=0),
        ),
    ]
