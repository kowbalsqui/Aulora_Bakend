# Generated by Django 5.1.2 on 2025-05-02 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Aulora_bakend', '0009_profesor_materia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modulo',
            name='contenido',
            field=models.TextField(),
        ),
    ]
