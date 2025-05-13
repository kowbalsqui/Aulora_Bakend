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
        queryset = Curso.objects.all()

        if user.rol == "2":  # Profesor
            try:
                materia = user.profesor.materia.strip()
                queryset = Curso.objects.filter(categoria_id__nombre__iexact=materia)
            except (AttributeError, Profesor.DoesNotExist):
                return Curso.objects.none()

        elif user.rol == "3":  # Estudiante
            if self.action == 'list':
                queryset = Curso.objects.exclude(inscripcion=user)

        # Aplicar límite si se pasa ?limit=5
        limit = self.request.query_params.get('limit')
        if limit and limit.isdigit():
            return queryset[:int(limit)]

        return queryset

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

        # Bloqueo para estudiantes no inscritos
        if user.rol == "3" and not instance.inscripcion.filter(id=user.id).exists():
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

        # Crear o asegurar progreso inicial
        progreso, created = Progreso.objects.get_or_create(
            usuario=user,
            curso=curso,
            defaults={'porcentaje': 0}
        )

        if created:
            print(f"🆕 Progreso creado para usuario {user.id} en curso {curso.id}")
        else:
            print(f"🔄 Progreso ya existía para usuario {user.id} en curso {curso.id}")

        # Verificar si ya había completado todos los demás cursos
        if progreso.porcentaje == 100:
            cursos_completados_ids = Progreso.objects.filter(
                usuario=user,
                porcentaje=100
            ).exclude(curso=curso).values_list('curso', flat=True)

            if curso.id not in cursos_completados_ids:
                user.cursos_completados += 1
                user.save()

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

        print(f"➡️ Módulo {modulo.id} completado del curso {curso.id} por {user.email}")

        ModuloCompletado.objects.get_or_create(usuario=user, modulo=modulo)

        total_modulos = curso.modulo_set.count()
        completados = ModuloCompletado.objects.filter(usuario=user, modulo__curso_id=curso.id).count()

        print(f"📊 Total módulos: {total_modulos}, Completados por usuario: {completados}")

        progreso, _ = Progreso.objects.get_or_create(usuario=user, curso=curso)
        progreso.porcentaje = round((completados / total_modulos) * 100) if total_modulos > 0 else 0
        progreso.save()

        print(f"✅ Progreso guardado: {progreso.porcentaje}%")

        if progreso.porcentaje == 100:
            print("🎯 Curso completado al 100%")

            ya_contado = Progreso.objects.filter(usuario=user, curso=curso, porcentaje=100).exists()
            if ya_contado:
                otros_completados = Progreso.objects.filter(usuario=user, porcentaje=100).exclude(curso=curso)
                print(f"🧮 Cursos ya contados (distintos): {otros_completados.values_list('curso', flat=True)}")

                if curso.id not in otros_completados.values_list('curso', flat=True):
                    user.cursos_completados += 1
                    user.save()
                    print(f"🏆 Usuario {user.email} ahora tiene {user.cursos_completados} cursos completados")

        for itinerario in curso.itinerario.filter(inscritos=user):
            actualizar_progreso_itinerario(user, itinerario)

        return Response({
            'detail': '✅ Módulo completado',
            'progreso_curso': progreso.porcentaje
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
    

    @action(detail=True, methods=['post'], url_path='inscribirse')
    def inscribirse(self, request, pk=None):
        itinerario = self.get_object()
        user = request.user

        if itinerario.inscritos.filter(id=user.id).exists():
            return Response({'detail': 'Ya estás inscrito en este itinerario.'}, status=400)

        itinerario.inscritos.add(user)
        return Response({'detail': 'Inscripción al itinerario completada.'}, status=200)

    @action(detail=True, methods=['post'], url_path='pagar')
    def pagar(self, request, pk=None):
        itinerario = self.get_object()
        user = request.user

        if itinerario.inscritos.filter(id=user.id).exists():
            return Response({'detail': 'Ya estás inscrito en este itinerario.'}, status=400)

        itinerario.inscritos.add(user)

        for curso in itinerario.cursos.all():
            # ✅ Crear inscripción usando el modelo relacional explícito
            Inscripcion.objects.get_or_create(usuario=user, curso=curso)
            Progreso.objects.get_or_create(usuario=user, curso=curso, defaults={'porcentaje': 0})

        return Response({'detail': 'Pago exitoso e inscripción completada.'}, status=200)


class MisCursosViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CursoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Curso.objects.filter(inscripciones__usuario=self.request.user)
    
class MisItinerariosViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ItinerarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print(self.request.user)
        return Itinerario.objects.filter(inscritos=self.request.user)
    
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

    
def actualizar_progreso_itinerario(usuario, itinerario):
    cursos = itinerario.cursos.all()
    total_cursos = cursos.count()

    if total_cursos == 0:
        itinerario.progreso = 0
    else:
        cursos_completados = Progreso.objects.filter(
            usuario=usuario,
            curso__in=cursos,
            porcentaje=100
        ).count()

        itinerario.progreso = int((cursos_completados / total_cursos) * 100)

    itinerario.save()

