from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico.')
        
        email = self.normalize_email(email)
        
        user = self.model(email=email, **extra_fields)

        # Guardar ambas contraseñas
        user.contrasena = password                    # texto plano
        user.set_password(password)                   # cifrado
        user.save(using=self._db)

        return user

    
    def create_superuser(self, email, password=None, **extra_fields): 
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    
# Modelo Usuario con los roles:
class Usuario(AbstractBaseUser, PermissionsMixin):
    ADMINISTRADOR = 1,
    PROFESOR = 2,
    ESTUDIANTE = 3
    
    ROLES = [
        ('admin', 'Administrador'),
        ('profesor', 'Profesor'),
        ('estudiante', 'Estudiante'),
    ]

    email = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=128)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    rol = models.CharField(max_length=20, choices=ROLES, default='admin')
    nombre = models.CharField(max_length=20)
    TIPO_CUENTA = [
        ('FR', 'Gratuita'), 
        ('PR', 'Premium'), 
    ]
    tipo_cuenta = models.CharField(choices=TIPO_CUENTA, max_length=50)
    
    # Campo añadido para la foto de perfil
    foto_perfil = models.ImageField(upload_to='usuarios/fotos/', blank=True, null=True, default='defaults/avatar.webp')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['contrasena']

    objects = UsuarioManager()

    def __str__(self): 
        return self.email
    
    def save(self, *args, **kwargs):
        # Nos aseguramos de que solo el usuario administrador tenga permisos de superusuario
        if self.rol == 'admin':
            self.is_staff = True
            self.is_superuser = True
        else:
            self.is_staff = False
            self.is_superuser = False
        
        super().save(*args, **kwargs)

# Clase del modelo de Rol Profesor
class Profesor(models.Model): 
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

# Clase del modelo de Rol Estudiante
class Estudiante(models.Model): 
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

# Clase del modelo de Categoría
class Categoria(models.Model): 
    nombre = models.CharField(max_length=15)

# Clase del modelo de Curso
class Curso(models.Model): 
    titulo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=300)    
    categoria_id = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    precio = models.IntegerField()
    inscripcion = models.ManyToManyField(Usuario, related_name='inscripcion', through='Inscripcion')

# Clase del modelo de Módulo
class Modulo(models.Model): 
    curso_id = models.ForeignKey(Curso, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=50)
    contenido = models.CharField(max_length=300)
    # Campos para almacenar un archivo (foto, video, documento) asociado al módulo
    archivo = models.FileField(upload_to='modulos/archivos/', blank=True, null=True)
    tipo_archivo = models.CharField(
        max_length=20,
        choices=[
            ('foto', 'Foto'),
            ('video', 'Video'),
            ('documento', 'Documento')
        ],
        blank=True,
        null=True
    )

# Clase del modelo de Pago
class Pago(models.Model): 
    usuario_id = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    curso_id = models.ForeignKey(Curso, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    METODO_PAGO = [
        ('TC', 'Tarjeta'),
        ('PP', 'PayPal'),
    ]
    metodo_pago = models.CharField(choices=METODO_PAGO, max_length=20)

# Clase del modelo de Inscripción, modelo relacional con Curso y Usuario
class Inscripcion(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='inscripciones')
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name='inscripciones')
    fecha_inscripcion = models.DateField(default=timezone.now)
