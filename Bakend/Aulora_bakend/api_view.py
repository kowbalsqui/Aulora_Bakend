from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.authentication import TokenAuthentication

# Asegúrate de tener definidos estos serializers en tu proyecto:
# UsuarioSerializerRegistro para la creación y UsuarioSerializer para mostrar datos.
from .serializers import *
from .models import *

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = UsuarioSerializerRegistro(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.save()  # ✅ Esto llama a tu método `create()` del serializer

            # Agrega a grupo, etc.
            rol = user.rol
            if rol == Usuario.PROFESOR:
                grupo = Group.objects.get(name='Profesores')
                user.groups.add(grupo)
                materia = request.data.get('materia')
                Profesor.objects.get_or_create(usuario=user, materia= materia)
            elif rol == Usuario.ESTUDIANTE:
                grupo = Group.objects.get(name='Estudiantes')
                user.groups.add(grupo)
                Estudiante.objects.get_or_create(usuario=user)

            # Token
            token, _ = Token.objects.get_or_create(user=user)
            usuarioSerializado = UsuarioSerializer(user)

            return Response({
                'message': 'Usuario registrado exitosamente',
                'token': token.key,
                'user': usuarioSerializado.data
            }, status=status.HTTP_201_CREATED)

        except Exception as error:
            return Response(
                {"detail": f"Ocurrió un error al crear el usuario: {repr(error)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Endpoint para iniciar sesión:
      - Recibe email y password.
      - Autentica el usuario.
      - Si es válido, obtiene o crea un token y retorna los datos del usuario.
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    user = authenticate(request, username=email, password=password)
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        usuarioSerializado = UsuarioSerializer(user)
        return Response({
            'message': 'Login exitoso',
            'token': token.key,
            'user': usuarioSerializado.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Endpoint para cerrar sesión:
      - Requiere autenticación.
      - Elimina el token del usuario autenticado.
    """
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Cierre de sesión exitoso'}, status=status.HTTP_200_OK)
    except Exception as error:
        return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def perfil_view(request):
    """
    Vista para ver o actualizar el perfil del usuario autenticado.
    """
    user = request.user

    if request.method == 'GET':
        serializer = UsuarioSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ModificaPerfilUsuario(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UsuarioSerializer(user).data)  # 🔁 CAMBIO AQUÍ
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Curso, Itinerario  # Asegúrate de tener importados tus modelos

# Api_view para obtener el precio del curso o itinerario sin usar el end-point creado

@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_precio_curso(request, id):
    curso = get_object_or_404(Curso, id=id)
    return Response({"precio": curso.precio})


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_precio_itinerario(request, id):
    itinerario = get_object_or_404(Itinerario, id=id)
    return Response({ "precio": itinerario.precio })

# Chat bot Aulora, asistente con preguntas predefinidas segun la interacción del usuario. 

@api_view(['POST'])
@permission_classes([AllowAny])
def chatbot_basico(request):
    pregunta = request.data.get('pregunta', '').lower()

     # Saludo
    if any(p in pregunta for p in ['hola', 'buenas', 'buenos dias', 'buenas tardes', 'buenas noches', 'que tal']):
        return Response({
            "respuesta": "¡Hola! Soy el chatbot de Aulora. ¿En qué puedo ayudarte?",
            "opciones": [
                "Cursos recomendados",
                "Cursos por temática",
                "Itinerarios recomendados",
                "Buscar curso barato",
                "Itinerarios por categoría"
            ]
        })

    # Qué eres / Cómo funcionas
    if any(p in pregunta for p in ['qué eres', 'que eres', 'quién eres', 'quien eres']):
        return Response({"respuesta": "Soy un chatbot diseñado para ayudarte a explorar cursos e itinerarios en Aulora."})

    if any(p in pregunta for p in ['cómo funcionas', 'como funcionas', 'cómo operas', 'como operas']):
        return Response({"respuesta": "Funciono respondiendo a tus preguntas sobre cursos, itinerarios, precios, recomendaciones y más. Solo escribe lo que necesites saber."})

    # Cursos recomendados
    if 'cursos recomendados' in pregunta:
        cursos = Curso.objects.all()[:3]
        nombres = ', '.join(curso.titulo for curso in cursos)
        return Response({"respuesta": f"Te recomiendo estos cursos: {nombres}"})

    # Recomendaciones por materia
    materias = ['historia', 'python', 'django', 'html', 'css', 'javascript', 'sql']
    for materia in materias:
        if materia in pregunta:
            cursos = Curso.objects.filter(titulo__icontains=materia).values_list('titulo', flat=True)
            if cursos:
                return Response({"respuesta": f"Te recomiendo estos cursos sobre {materia.capitalize()}: {', '.join(cursos)}"})
            return Response({"respuesta": f"No encontré cursos sobre {materia}."})

    # Curso aparece en itinerario
    if 'curso' in pregunta and 'itinerario' in pregunta:
        for curso in Curso.objects.all():
            if curso.titulo.lower() in pregunta:
                itinerarios = Itinerario.objects.filter(cursos=curso).values_list('titulo', flat=True)
                if itinerarios:
                    return Response({"respuesta": f"El curso {curso.titulo} aparece en los itinerarios: {', '.join(itinerarios)}"})
                return Response({"respuesta": f"El curso {curso.titulo} no está en ningún itinerario."})

    # Curso barato
    if 'curso' in pregunta and any(p in pregunta for p in ['barato', 'económico', 'menor precio']):
        curso = Curso.objects.order_by('precio').first()
        return Response({"respuesta": f"El curso más barato es {curso.titulo} y cuesta {curso.precio}€"})

    # Itinerarios recomendados
    if 'itinerarios recomendados' in pregunta:
        itinerarios = Itinerario.objects.all()[:3]
        titulos = ', '.join(it.titulo for it in itinerarios)
        return Response({"respuesta": f"Te recomiendo estos itinerarios: {titulos}"})

    # Itinerarios con curso de X categoría
    if 'itinerario' in pregunta and any(p in pregunta for p in ['categoría', 'categoria']):
        for cat in Categoria.objects.all():
            if cat.nombre.lower() in pregunta:
                itinerarios = Itinerario.objects.filter(cursos__categoria=cat).distinct()
                if itinerarios:
                    return Response({"respuesta": f"Los itinerarios con cursos de {cat.nombre} son: {', '.join(i.titulo for i in itinerarios)}"})
                return Response({"respuesta": f"No hay itinerarios con cursos de la categoría {cat.nombre}."})

    # Itinerario barato
    if 'itinerario' in pregunta and any(p in pregunta for p in ['barato', 'económico', 'menor precio']):
        itinerario = Itinerario.objects.order_by('precio').first()
        return Response({"respuesta": f"El itinerario más barato es {itinerario.titulo} y cuesta {itinerario.precio}€"})

    # Catch-all
    return Response({"respuesta": "No entendí tu pregunta. Puedes preguntarme por cursos, itinerarios, precios o recomendaciones."})