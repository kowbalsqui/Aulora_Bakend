from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
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

@api_view(['POST'])
@permission_classes([AllowAny])
def chatbot_basico(request):
    pregunta = request.data.get('pregunta', '').lower()

    #Saludo

    if any(p in pregunta for p in ['hola', 'buenas', 'buenos dias', 'buenas tardes' 'buenas noches', 'que tal']):
        return Response ({"respuesta": "Hola buenas señorito/a estudiante, soy un Chat-Bot programado para tu disposición, perdoname si no entiendo algunas palabras, todavia estoy en fase beta <3"})
    
    # Agradecimientos 

    if any(p in pregunta for p in ['muchas gracias', 'gracias', 'ty', 'grax']):
        return Response ({"respuesta": "A ti por confiar en Aulora, tu chat-bot que te ayudara en todo lo que pueda :)"})
    
    # 1. Cursos disponibles
    if any(p in pregunta for p in ["cursos", "curso"]) and any(p in pregunta for p in ["hay", "tenéis", "tienes", "disponibles", "ofreces", "ofrecéis"]):
        cursos = Curso.objects.all().values_list('titulo', flat=True)
        return Response({"respuesta": f"Los cursos disponibles son: {', '.join(cursos)}"})

    # 2. Precio de un curso
    if any(p in pregunta for p in ["cuánto cuesta", "precio", "vale"]):
        for curso in Curso.objects.all():
            if curso.titulo.lower() in pregunta:
                return Response({"respuesta": f"El curso {curso.titulo} cuesta {curso.precio}€"})
        return Response({"respuesta": "No encontré ese curso."})

    # 3. Itinerarios que incluyen un curso
    if "itinerario" in pregunta and any(p in pregunta for p in ["incluyen", "contienen", "tienen"]):
        for curso in Curso.objects.all():
            if curso.titulo.lower() in pregunta:
                itinerarios = Itinerario.objects.filter(cursos=curso).values_list('titulo', flat=True)
                if itinerarios:
                    return Response({"respuesta": f"Los itinerarios que incluyen {curso.titulo} son: {', '.join(itinerarios)}"})
                return Response({"respuesta": f"No hay itinerarios con {curso.titulo}."})

    # 4. Recomendaciones generales o por categoría
    if any(p in pregunta for p in ["recomiendas", "aconsejas", "empezar", "iniciar"]):
        categorias = Categoria.objects.all()
        for cat in categorias:
            if cat.nombre.lower() in pregunta:
                curso = Curso.objects.filter(categoria_id=cat.id).first()
                if curso:
                    return Response({"respuesta": f"Te recomiendo empezar con el curso: {curso.titulo}, dentro de la categoría {cat.nombre}."})
                return Response({"respuesta": f"No encontré cursos en la categoría {cat.nombre}."})

        # Recomendación genérica si no se menciona ninguna categoría
        return Response({
            "respuesta": "Si estás empezando, te recomiendo dependiendo de lo que quieras o estés interesado/a. Pero una base de Matemáticas siempre viene bien."
        })

    # Categorias disponibles

    if any(p in pregunta for p in ['categorias', 'categorías', 'tipos', 'secciones', 'tipo de cursos', 'temas']):
        categorias = Categoria.objects.all()
        if categorias.exists():
            nombres = [cat.nombre for cat in categorias]
            return Response({"respuesta": f"Las categorías disponibles son: {', '.join(nombres)}"})
        else:
            return Response({"respuesta": "No hay categorías disponibles por ahora."})

    # 5. Cursos por temática
    if "curso" in pregunta and any(p in pregunta for p in ["de", "sobre", "acerca de"]):
        temas = ["historia", "python", "django", "html", "css", "javascript", "sql"] #AMPLIAR
        for tema in temas:
            if tema in pregunta:
                cursos = Curso.objects.filter(titulo__icontains=tema).values_list('titulo', flat=True)
                if cursos:
                    return Response({"respuesta": f"Los cursos sobre {tema.capitalize()} son: {', '.join(cursos)}"})
                return Response({"respuesta": f"No tenemos cursos específicamente sobre {tema}."})

    # 6. Qué es un itinerario
    if any(p in pregunta for p in ["qué es un itinerario", "que es un itinerario", "para qué sirve un itinerario"]):
        return Response({"respuesta": "Un itinerario es un conjunto de cursos organizados para ayudarte a aprender un tema de forma progresiva."})

    # 7. Cómo apuntarse
    if any(p in pregunta for p in ["apuntarme", "inscribirme", "registrarme", "unirme", "cómo me apunto"]):
        return Response({"respuesta": "Para apuntarte a un curso o itinerario, haz clic en el botón 'Apuntarme' desde la página principal."})

    # 8. Cursos gratuitos
    if any(p in pregunta for p in ["gratuitos", "gratis", "sin pagar", "costo cero"]):
        cursos_gratis = Curso.objects.filter(precio=0).values_list('titulo', flat=True)
        if cursos_gratis:
            return Response({"respuesta": f"Estos cursos son gratuitos: {', '.join(cursos_gratis)}"})
        return Response({"respuesta": "Actualmente no hay cursos gratuitos disponibles."})

    # 9. Cursos con prácticas
    if any(p in pregunta for p in ["práctica", "prácticas", "ejercicios", "proyectos"]):
        return Response({"respuesta": "Muchos cursos incluyen ejercicios prácticos, especialmente los de programación y desarrollo web."})

    # 10. Acceso desde el móvil
    if any(p in pregunta for p in ["móvil", "celular", "teléfono", "tablet"]):
        return Response({"respuesta": "Sí, puedes acceder a Aulora desde cualquier dispositivo con conexión a internet, incluyendo móviles."})

    # 11. Experiencia previa
    if any(p in pregunta for p in ["experiencia previa", "necesito saber", "ya tengo que saber", "nivel necesario"]):
        return Response({"respuesta": "No necesitas experiencia previa para la mayoría de los cursos. Están diseñados para aprender desde cero."})

    # 12. Duración del curso
    if any(p in pregunta for p in ["cuánto dura", "duración", "tiempo que lleva"]):
        for curso in Curso.objects.all():
            if curso.titulo.lower() in pregunta and curso.duracion:
                return Response({"respuesta": f"El curso {curso.titulo} tiene una duración estimada de {curso.duracion} horas."})
        return Response({"respuesta": "No encontré la duración de ese curso."})

    # 13. Preguntas confidenciales
    if any(p in pregunta for p in ["usuario", "usuarios", "profesor", "profesores", "estudiante", "estudiantes"]):
        return Response({"respuesta": "No puedo darte información personal de los usuarios por razones de privacidad."})

    # 14. Catch-all
    return Response({"respuesta": "No entendí tu pregunta. Puedes preguntarme por cursos, itinerarios, precios o recomendaciones."})