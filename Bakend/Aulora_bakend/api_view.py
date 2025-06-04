import requests
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import *


# Asegúrate de tener definidos estos serializers en tu proyecto:
# UsuarioSerializerRegistro para la creación y UsuarioSerializer para mostrar datos.
from .serializers import *
from .models import *

def verificar_captcha(token):
    secret_key = '6LdmOFQrAAAAAFmdvYOxEMhQ8LXsJ_YKIRBIZgh3'
    url = 'https://www.google.com/recaptcha/api/siteverify'
    data = {
        'secret': secret_key,
        'response': token
    }
    respuesta = requests.post(url, data=data)
    resultado = respuesta.json()
    return resultado.get('success', False)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):

    #Verificar el captcha
    captcha_token = request.data.get('captcha')
    if not captcha_token or not verificar_captcha(captcha_token):
        return Response({'detail': 'Captcha inválido'}, status=status.HTTP_400_BAD_REQUEST)

    #Registro del usuario
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


#Api_view para la recuperacion de la contraseña parte 1: verificacion del email del usuario con la base de datos.

@api_view(['POST'])
@permission_classes([AllowAny])
def verificar_email(request):
    email = request.data.get('email')
    if not email:
        return Response({'detail': 'Email requerido'}, status=400)

    if Usuario.objects.filter(email=email).exists():
        return Response({'detail': 'Email válido'}, status=200)
    else:
        return Response({'detail': 'Email no registrado'}, status=404)

    
# Api_view recuperacion de contraseña parte 2, redireccion de página y cambio de contraseña.

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    email = request.data.get('email')
    new_password = request.data.get('password')

    try:
        user = Usuario.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Contraseña cambiada correctamente'})
    except Usuario.DoesNotExist:
        return Response({'detail': 'Usuario no encontrado'}, status=404)

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
    opcion = request.data.get('pregunta', '').strip().lower()

    # INICIO
    if opcion == 'hola':
        return Response({
            "respuesta": "¡Hola! Soy el chatbot de Aulora. ¿Qué deseas hacer?",
            "opciones": [
                "Cursos recomendados",
                "Cursos por temática",
                "Itinerarios recomendados",
                "Buscar curso barato",
                "Buscar itinerario barato",
                "Itinerarios por categoría"
            ]
        })

    # CURSOS RECOMENDADOS
    elif opcion == 'cursos recomendados':
        cursos = Curso.objects.all()[:3]
        nombres = ', '.join(curso.titulo for curso in cursos)
        return Response({
            "respuesta": f"Te recomiendo estos cursos: {nombres}",
            "opciones": ["Volver al inicio"]
        })

    # ITINERARIOS RECOMENDADOS
    elif opcion == 'itinerarios recomendados':
        itinerarios = Itinerario.objects.all()[:3]
        nombres = ', '.join(it.titulo for it in itinerarios)
        return Response({
            "respuesta": f"Te recomiendo estos itinerarios: {nombres}",
            "opciones": ["Volver al inicio"]
        })

    # CURSO MÁS BARATO
    elif opcion == 'buscar curso barato':
        curso = Curso.objects.order_by('precio').first()
        if curso:
            return Response({
                "respuesta": f"El curso más barato es '{curso.titulo}' y cuesta {curso.precio}€.",
                "opciones": ["Volver al inicio"]
            })
        else:
            return Response({
                "respuesta": "No hay cursos disponibles.",
                "opciones": ["Volver al inicio"]
            })

    # ITINERARIO MÁS BARATO
    elif opcion == 'buscar itinerario barato':
        itinerario = Itinerario.objects.order_by('precio').first()
        if itinerario:
            return Response({
                "respuesta": f"El itinerario más barato es '{itinerario.titulo}' y cuesta {itinerario.precio}€.",
                "opciones": ["Volver al inicio"]
            })
        else:
            return Response({
                "respuesta": "No hay itinerarios disponibles.",
                "opciones": ["Volver al inicio"]
            })

    # CURSOS POR TEMÁTICA (categorías de cursos)
    elif opcion == 'cursos por temática':
        categorias = Categoria.objects.all().values_list('nombre', flat=True)
        return Response({
            "respuesta": "Elige una temática:",
            "opciones": list(categorias) + ["Volver al inicio"]
        })

    # ITINERARIOS POR CATEGORÍA (categorías de cursos también)
    elif opcion == 'itinerarios por categoría':
        categorias = Categoria.objects.all().values_list('nombre', flat=True)
        return Response({
            "respuesta": "Selecciona una categoría:",
            "opciones": list(categorias) + ["Volver al inicio"]
        })

    # OPCIÓN DE VOLVER
    elif opcion == 'volver al inicio':
        return Response({
            "respuesta": "¿Qué deseas hacer?",
            "opciones": [
                "Cursos recomendados",
                "Cursos por temática",
                "Itinerarios recomendados",
                "Buscar curso barato",
                "Buscar itinerario barato",
                "Itinerarios por categoría"
            ]
        })
    
    elif Categoria.objects.filter(nombre__iexact=opcion).exists():
        cat = Categoria.objects.get(nombre__iexact=opcion)
        cursos = Curso.objects.filter(categoria_id=cat.id)
        itinerarios = Itinerario.objects.filter(cursos__categoria_id=cat.id).distinct()

        if cursos.exists():
            return Response({
                "respuesta": f"Cursos en la categoría {cat.nombre}: {', '.join(c.titulo for c in cursos)}",
                "opciones": ["Volver al inicio"]
            })

        elif itinerarios.exists():
            return Response({
                "respuesta": f"Itinerarios con cursos de la categoría {cat.nombre}: {', '.join(i.titulo for i in itinerarios)}",
                "opciones": ["Volver al inicio"]
            })

        else:
            return Response({
                "respuesta": f"No hay cursos ni itinerarios en la categoría {cat.nombre}.",
                "opciones": ["Volver al inicio"]
            })
