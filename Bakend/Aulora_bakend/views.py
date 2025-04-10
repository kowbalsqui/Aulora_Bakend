from rest_framework import viewsets
from .models import *
from .serializers import *
from django.shortcuts import render,redirect
from rest_framework.permissions import IsAuthenticated


def inicio(request):
    #SESION
    return render(request, 'inicioPadre.html')
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        print("🔎 Usuario logueado:", user.email)
        print("🔎 Rol:", user.rol)

        #Si el usuario es un profesor, filtra los cursos por la materia que imparte comparando con el campo de la categoria del curso
        if user.rol == "2":
            profesor = user.profesor
            materia = profesor.materia
            print("🔎 Materia del profesor:", materia)

            cursos = Curso.objects.filter(categoria_id__nombre__iexact=materia)
            print("🔎 Cursos encontrados:", cursos.count())

            for curso in cursos:
                print(f"  - {curso.titulo} ({curso.categoria_id.nombre})")

            return cursos
        return super().get_queryset()

class ModuloViewSet(viewsets.ModelViewSet):
    queryset = Modulo.objects.all()
    serializer_class = ModuloSerializer

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