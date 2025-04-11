from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *
from .api_view import *

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'cursos', CursoViewSet)
router.register(r'modulos', ModuloViewSet)
router.register(r'pagos', PagoViewSet)
router.register(r'inscripciones', InscripcionViewSet)
router.register(r'itinerarios', ItinerarioViewSet)
router.register(r'mis-cursos', MisCursosViewSet, basename='mis-cursos')
router.register(r'mis-itinerarios', MisItinerariosViewSet, basename='mis-itinerarios')
router.register(r'explorar-cursos', CursoExploraViewSet, basename='explorar-cursos')
router.register(r'explorar-itinerarios', ItinerarioExplorarViewSet, basename='explorar-itinerarios')

urlpatterns = [
    path('', include(router.urls)),  # <- solo esto
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('perfil/', perfil_view, name= 'perfil'),
]
