from rest_framework import serializers
from .models import *

# Serializer para Usuario
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'contrasena', 'nombre', 'tipo_cuenta', 'foto_perfil', 'rol']

    def create(self, validated_data):
        password = validated_data.pop('contrasena')  # Extraemos la contraseña
        user = Usuario.objects.create_user(password=password, **validated_data)
        return user


# Serializer para Categoría
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']

# Serializer para Curso
class CursoSerializer(serializers.ModelSerializer):
    categoria_id = CategoriaSerializer()
    inscripcion = UsuarioSerializer(many=True, read_only=True)

    class Meta:
        model = Curso
        fields = ['id', 'titulo', 'descripcion', 'categoria_id', 'precio', 'inscripcion']

# Serializer para Modulo
class ModuloSerializer(serializers.ModelSerializer):
    curso_id = CursoSerializer()

    class Meta:
        model = Modulo
        fields = ['id', 'curso_id', 'titulo', 'contenido', 'tipo_archivo', 'archivo']

# Serializer para Pago
class PagoSerializer(serializers.ModelSerializer):
    usuario_id = UsuarioSerializer()
    curso_id = CursoSerializer()

    class Meta:
        model = Pago
        fields = ['id', 'usuario_id', 'curso_id', 'cantidad', 'metodo_pago']

# Serializer para Inscripción
class InscripcionSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer()
    curso = CursoSerializer()

    class Meta:
        model = Inscripcion
        fields = ['id', 'usuario', 'curso', 'fecha_inscripcion']
    
from rest_framework import serializers
from .models import Usuario

class UsuarioSerializerRegistro(serializers.Serializer):
    nombre = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True, max_length=100)
    password2 = serializers.CharField(write_only=True, max_length=100)
    rol = serializers.IntegerField()
    tipo_cuenta = serializers.ChoiceField(choices=Usuario.TIPO_CUENTA)
    foto_perfil = serializers.ImageField(required=False, allow_null=True)

    def validate_email(self, email):
        if Usuario.objects.filter(email=email).exists():
            raise serializers.ValidationError('Ya existe un usuario con ese email')
        return email

    def validate_password2(self, password2):
        password1 = self.initial_data.get('password1')
        if password1 != password2:
            raise serializers.ValidationError('Las contraseñas no coinciden')
        return password2

    def validate_password1(self, password1):
        if len(password1) < 8:
            raise serializers.ValidationError('La contraseña debe tener al menos 8 caracteres')
        return password1

    def validate_nombre(self, nombre):
        if Usuario.objects.filter(nombre=nombre).exists():
            raise serializers.ValidationError('Ya existe un usuario con ese nombre de usuario')
        return nombre

    def create(self, validated_data):
        # Extraer y remover contraseñas
        raw_password = validated_data.pop('password1')
        validated_data.pop('password2')

        # Guardar la contraseña sin cifrar en el campo personalizado 'contraseña'
        validated_data['contrasena'] = raw_password

        # Crear el usuario
        user = Usuario(**validated_data)
        user.set_password(raw_password)
        user.save()
        return user

