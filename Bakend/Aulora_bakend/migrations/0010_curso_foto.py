# Generated by Django 5.1.8 on 2025-04-11 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Aulora_bakend', '0009_profesor_materia'),
    ]

    operations = [
        migrations.AddField(
            model_name='curso',
            name='foto',
            field=models.ImageField(blank=True, default='defaults/course.webp', null=True, upload_to='cursos/fotos/'),
        ),
    ]
