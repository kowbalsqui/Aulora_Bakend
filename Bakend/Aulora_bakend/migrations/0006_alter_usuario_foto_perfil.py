# Generated by Django 5.1.8 on 2025-04-10 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Aulora_bakend', '0005_rename_contraseña_usuario_contrasena'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='foto_perfil',
            field=models.ImageField(blank=True, default='defaults/avatar.webp', null=True, upload_to='usuarios/fotos/'),
        ),
    ]
