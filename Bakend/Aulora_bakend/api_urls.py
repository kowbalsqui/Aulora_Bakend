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
router.register(r'progresos', ProgresoCursoViewSet, basename='progreso')
router.register(r'itinerarios', ItinerarioViewSet, basename='itinerario')


urlpatterns = [
    path('', include(router.urls)),  # <- solo esto
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('perfil/', perfil_view, name= 'perfil'),
    path('chatbot/', chatbot_basico),
    path('cursos/<int:id>/precio/', obtener_precio_curso),
    path('itinerarios/<int:id>/precio/', obtener_precio_itinerario),
    path('verificar-email/', verificar_email),
    path('reset-password/', reset_password),
]