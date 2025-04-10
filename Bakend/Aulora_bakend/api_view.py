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
        serializer = GetDatosPerfil(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ModificaPerfilUsuario(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

