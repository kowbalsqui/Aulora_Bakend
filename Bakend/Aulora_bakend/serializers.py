from rest_framework import serializers
from .models import *

# Serializer para Usuario
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'contrasena', 'nombre', 'tipo_cuenta','cursos_completados', 'foto_perfil', 'rol']

    def create(self, validated_data):
        password = validated_data.pop('contrasena')  # Extraemos la contraseña
        user = Usuario.objects.create_user(password=password, **validated_data)
        return user


# Serializer para Categoría
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']

# Serializer para Modulo
class ModuloSerializer(serializers.ModelSerializer):
    completado = serializers.SerializerMethodField()

    class Meta:
        model = Modulo
        fields = ['id', 'curso_id', 'titulo', 'contenido', 'completado',  'tipo_archivo', 'archivo']


    def get_completado(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        return user and user.is_authenticated and ModuloCompletado.objects.filter(usuario=user, modulo=obj).exists()

# Serializer para Curso
class CursoSerializer(serializers.ModelSerializer):
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all()
    )
    inscrito = serializers.SerializerMethodField()


    modulos = ModuloSerializer(many=True, read_only=True, source='modulo_set')
    inscritos = serializers.PrimaryKeyRelatedField(many=True, read_only=True, source='inscripciones')
    categoria_nombre = serializers.CharField(source='categoria_id.nombre', read_only=True)
    inscripcion = UsuarioSerializer(many=True, read_only=True)
    progreso_usuario = serializers.SerializerMethodField()  # ✅ nuevo campo

    class Meta:
        model = Curso
        fields = [
            'id', 'titulo', 'descripcion', 'categoria_id', 'precio', 'inscripcion',
            'foto', 'categoria_nombre', 'modulos', 'inscritos', 'progreso_usuario', 'inscrito' # ✅ añadir aquí también
        ]

    def get_progreso_usuario(self, obj):
        user = self.context['request'].user
        if user.is_authenticated and user.rol == "3":
            progreso = Progreso.objects.filter(usuario=user, curso=obj).first()
            return progreso.porcentaje if progreso else 0
        return None
    
    def get_inscrito(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and obj.inscripcion.filter(id=user.id).exists()


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


# Serializer para Itinerario
class ItinerarioSerializer(serializers.ModelSerializer):
    cursos = serializers.PrimaryKeyRelatedField(queryset=Curso.objects.all(), many=True, write_only=True)
    cursos_detalles = CursoSerializer(source='cursos', many=True, read_only=True)
    inscrito = serializers.SerializerMethodField()

    class Meta:
        model = Itinerario
        fields = [
            'id', 'titulo', 'descripcion', 'progreso',
            'precio', 'cursos', 'cursos_detalles', 'inscrito', 'inscritos'
        ]

    def get_inscrito(self, obj):
        user = self.context['request'].user
        return obj.inscritos.filter(id=user.id).exists() if user.is_authenticated else False

    def create(self, validated_data):
        cursos = validated_data.pop('cursos', [])
        itinerario = Itinerario.objects.create(**validated_data)
        for curso in cursos:
            Itinerario_curso.objects.create(itinerario_id=itinerario, curso=curso)
        return itinerario
    
    def update(self, instance, validated_data):
        cursos = validated_data.pop('cursos', None)

        # Actualizar campos simples
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar relación M2M a través del modelo intermedio
        if cursos is not None:
            instance.cursos.clear()
            for curso in cursos:
                Itinerario_curso.objects.create(itinerario_id=instance, curso=curso)

        return instance



#Serializer para el regustro de los usuarios
class UsuarioSerializerRegistro(serializers.Serializer):
    nombre = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True, max_length=100)
    password2 = serializers.CharField(write_only=True, max_length=100)
    rol = serializers.IntegerField()
    tipo_cuenta = serializers.ChoiceField(choices=Usuario.TIPO_CUENTA)
    foto_perfil = serializers.ImageField(required=False, allow_null=True)
    materia = serializers.CharField(max_length=50, required=False, allow_blank=True)

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

        #Guarda el campo de la materia si tiene o viene algo 
        materia = validated_data.pop('materia', None)  

        # Crear el usuario
        user = Usuario(**validated_data)
        user.set_password(raw_password)
        user.save()

        if user.rol == 2 and materia:
            Profesor.objects.create(usuario=user, materia=materia)
        return user

#Serializer para el modificar perfil del usuario

class ModificaPerfilUsuario(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['nombre', 'foto_perfil', 'tipo_cuenta', 'contrasena']
        extra_kwargs = {
            'contrasena': {'required': False, 'write_only': True}
        }

    def update(self, instance, validated_data):
        password = validated_data.pop('contrasena', None)
        nombre = validated_data.pop('nombre', None)
        foto = validated_data.pop('foto_perfil', None)
        cuenta = validated_data.pop('tipo_cuenta', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
            instance.contrasena = password

        if nombre:
            instance.nombre = nombre

        if foto:
            instance.foto_perfil = foto

        if cuenta:
            instance.tipo_cuenta = cuenta

        instance.save()
        return instance
    
class GetDatosPerfil(serializers.ModelSerializer):
    class Meta: 
        model= Usuario
        fields= ['nombre', 'foto_perfil', 'contrasena', 'tipo_cuenta', 'cursos_completados']
        extra_kwargs = {
            'contrasena': {'write_only': True}
        }

class ProgresoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progreso
        fields = ['id', 'usuario', 'curso', 'porcentaje', 'actualizado']

    def get_queryset(self):
        return Progreso.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
