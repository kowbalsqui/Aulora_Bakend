from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, filters
from .models import *
from .serializers import *
from django.shortcuts import render,redirect
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend



def inicio(request):
    #SESION
    return render(request, 'inicioPadre.html')
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # 👨‍🏫 Filtrado para profesores
        if user.rol == "2":
            try:
                materia = user.profesor.materia.strip()
                print(f"🔍 Filtrando cursos por materia: {materia}")
                return Curso.objects.filter(categoria__nombre__iexact=materia)
            except Profesor.DoesNotExist:
                print("⚠️ Profesor no tiene materia asignada")
                return Curso.objects.none()

        # 👨‍🎓 Estudiantes y otros ven todos
        return Curso.objects.exclude(inscripcion=user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        # ❌ Bloqueo para estudiantes no inscritos
        if user.rol == "3":
            if not instance.inscripcion.filter(id=user.id).exists():
                return Response(
                    {'detail': 'No estás inscrito en este curso.'},
                    status=status.HTTP_403_FORBIDDEN
                )

        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='inscribirse')
    def inscribirse(self, request, pk=None):
        print(f"📥 Intentando inscribir al curso ID: {pk}")

        try:
            curso = Curso.objects.get(pk=pk)
        except Curso.DoesNotExist:
            print("❌ Curso no encontrado")
            return Response({'detail': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        if curso.inscripcion.filter(id=user.id).exists():
            print("⚠️ Usuario ya inscrito en el curso.")
            return Response({'detail': 'Ya estás inscrito.'}, status=status.HTTP_400_BAD_REQUEST)

        curso.inscripcion.add(user)
        return Response({'detail': 'Inscripción exitosa'}, status=status.HTTP_200_OK)

class ModuloViewSet(viewsets.ModelViewSet):
    queryset = Modulo.objects.all()
    serializer_class = ModuloSerializer
    permission_classes = [IsAuthenticated]

class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer

class InscripcionViewSet(viewsets.ModelViewSet):
    queryset = Inscripcion.objects.all()
    serializer_class = InscripcionSerializer

class ItinerarioViewSet(viewsets.ModelViewSet):
    queryset = Itinerario.objects.all()
    serializer_class = ItinerarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.rol == "2":
            materia = user.materia
            return Itinerario.objects.filter(cursos__categoria_id__nombre__iexact=materia).distinct()
        return super().get_queryset()

class MisCursosViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CursoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Curso.objects.filter(inscripciones__usuario=self.request.user)
    
class MisItinerariosViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ItinerarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Itinerario.objects.filter(cursos__inscripciones__usuario=self.request.user)
    
class CursoExploraViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [AllowAny] # Permitir acceso a todos los usuarios, incluso no autenticados

    # Campos para búsqueda libre (por texto)
    search_fields = ['titulo', 'descripcion', 'categoria_id__nombre']

    # Filtros exactos por campo
    filterset_fields = ['categoria_id']

    # Ordenación
    ordering_fields = ['precio', 'titulo']

class ItinerarioExplorarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Itinerario.objects.all()
    serializer_class = ItinerarioSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [AllowAny] # Permitir acceso a todos los usuarios, incluso no autenticados

    # Campos para búsqueda libre (por texto)
    search_fields = ['titulo', 'descripcion']

    # Ordenación
    ordering_fields = ['titulo']