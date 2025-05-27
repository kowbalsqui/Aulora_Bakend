# Aulora_Bakend

Aulora - Despliegue con Docker Hub

Este tutorial te explica cómo desplegar la aplicación web **Aulora** usando las imágenes disponibles en Docker Hub, sin necesidad de clonar el repositorio.

---

Requisitos

- Tener instalado Docker y Docker Compose
- Acceso a Internet

---

Paso 1: Crear un archivo `docker-compose.yml`

Crea un archivo llamado `docker-compose.yml` con el siguiente contenido:

```yaml
version: '3.8'

services:
  backend:
    image: carlospereafiguera/aulora-backend:dev
    container_name: aulora_backend
    ports:
      - "8000:8000"
    networks:
      - aulora_net

  frontend:
    image: carlospereafiguera/aulora-frontend:dev
    container_name: aulora_frontend
    ports:
      - "4200:80"
    networks:
      - aulora_net
    depends_on:
      - backend

networks:
  aulora_net:
```

---

Paso 2: Levantar la aplicación

Desde la terminal, en la misma carpeta donde guardaste el archivo:

```bash
docker-compose up
```

---

Paso 3: Accede desde tu navegador

- Frontend (Angular): [http://localhost:4200](http://localhost:4200)
- Backend (API Django): [http://localhost:8000](http://localhost:8000)

---

Notas

- Esta versión de `:dev` está configurada para desarrollo local. El frontend hace peticiones a `http://localhost:8000`.
- Asegúrate de que ningún otro proceso esté usando los puertos 4200 o 8000.
- Para producción se recomienda usar una versión que conecte usando `http://aulora_backend:8000`.

---

Para detener los contenedores

```bash
docker-compose down
```

---

¡Eso es todo! Aulora estará corriendo localmente usando las imágenes Docker públicas de [carlospereafiguera](https://hub.docker.com/u/carlospereafiguera) 🎉