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
    permission_classes = [AllowAny]
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.rol == "2":
            try:
                materia = user.profesor.materia.strip()
                return Curso.objects.filter(categoria_id__nombre__iexact=materia)
            except (AttributeError, Profesor.DoesNotExist):
                return Curso.objects.none()
        if user.rol == "3":
            if self.action == 'list':
                return Curso.objects.exclude(inscripcion=user)
            return Curso.objects.all()
        return Curso.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'profesor'):
            materia = user.profesor.materia.strip()
            categoria = Categoria.objects.filter(nombre__iexact=materia).first()
            if categoria:
                serializer.save(categoria_id=categoria)
                print(f"✅ Curso creado para materia: {materia} → categoría: {categoria}")

            else:
                raise serializers.ValidationError("No se encontró una categoría que coincida con tu materia.")
        else:
            raise serializers.ValidationError("Solo los profesores pueden crear cursos.")

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

        # ⏳ Crear o asegurar progreso inicial
        progreso, created = Progreso.objects.get_or_create(
            usuario=user,
            curso=curso,
            defaults={'porcentaje': 0}
        )

        if created:
            print(f"🆕 Progreso creado para usuario {user.id} en curso {curso.id}")
        else:
            print(f"🔄 Progreso ya existía para usuario {user.id} en curso {curso.id}")

        return Response({'detail': 'Inscripción exitosa'}, status=status.HTTP_200_OK)

class ModuloViewSet(viewsets.ModelViewSet):
    queryset = Modulo.objects.all()
    serializer_class = ModuloSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='completar')
    def completar(self, request, pk=None):
        user = request.user
        modulo = self.get_object()
        curso = modulo.curso_id

        # Obtener total de módulos del curso
        total_modulos = curso.modulo_set.count()

        # Aquí puedes definir cómo contar cuántos ha completado el usuario
        # Por ahora, asumimos que cada llamada suma un módulo
        progreso, _ = Progreso.objects.get_or_create(usuario=user, curso=curso)
        modulos_actuales = curso.modulo_set.count()

        # Por ejemplo, si el usuario completa un módulo, suponemos que avanza en +1 módulo
        # Incrementamos un % fijo por módulo (esto NO es persistente si no guardas qué completó)
        porcentaje_unitario = 100 / total_modulos
        nuevo_porcentaje = min(100, progreso.porcentaje + porcentaje_unitario)
        progreso.porcentaje = round(nuevo_porcentaje)
        progreso.save()

        return Response({
            'detail': '✅ Módulo marcado como completado',
            'nuevo_progreso': progreso.porcentaje
        })

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
            materia = user.profesor.materia
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


class ProgresoCursoViewSet(viewsets.ModelViewSet):
    serializer_class = ProgresoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Progreso.objects.filter(usuario=self.request.user)
