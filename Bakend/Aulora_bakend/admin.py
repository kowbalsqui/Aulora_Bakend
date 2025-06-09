from django.contrib import admin
from .models import *

admin.site.register(Usuario)
admin.site.register(Curso)
admin.site.register(Itinerario)
admin.site.register(Modulo)
admin.site.register(Categoria)
admin.site.register(Inscripcion)
admin.site.register(Pago)
admin.site.register(Itinerario_curso)
admin.site.register(Progreso)
admin.site.register(ModuloCompletado)


# Register your models here.