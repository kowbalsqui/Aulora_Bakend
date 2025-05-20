Aulora - Despliegue con Docker Hub

Este tutorial te explica cómo desplegar la aplicación web Aulora usando las imágenes disponibles en Docker Hub, sin necesidad de clonar el repositorio.

Requisitos

    Tener instalado Docker y Docker Compose
    Acceso a Internet

Paso 1: Crear un archivo docker-compose.yml

Crea un archivo llamado docker-compose.yml con el siguiente contenido:

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

Paso 2: Levantar la aplicación

Desde la terminal, en la misma carpeta donde guardaste el archivo:

docker-compose up

Paso 3: Accede desde tu navegador

    Frontend (Angular): http://localhost:4200
    Backend (API Django): http://localhost:8000

Notas

    Esta versión de :dev está configurada para desarrollo local. El frontend hace peticiones a http://localhost:8000.
    Asegúrate de que ningún otro proceso esté usando los puertos 4200 o 8000.
    Para producción se recomienda usar una versión que conecte usando http://aulora_backend:8000.

Para detener los contenedores

docker-compose down

¡Eso es todo! Aulora estará corriendo localmente usando las imágenes Docker públicas de carlospereafiguera

Para obtener los archivos del proyecto y poder programarlos a tu manera, puedes descargarte los repositorios o clonarlos y hacer lo siguiente:

Paso 1: Clonar los repositorios:

Nos iremos a github y dentro de el, nos vamos al proyecto los cuales son los siguientes:

Frontend: https://github.com/kowbalsqui/Aulora_Fronted.git Bakend: https://github.com/kowbalsqui/Aulora_Bakend.git

Nos vamos al apartado donde dice "code" y le damos a ssh.

Le damos a una terminal e ingresamos el siguiente comando:

    git clone "ssh del codigo del proyecto"

Una vez los tenemos los dos, deberemos de meternos en el bakend y haremos los siguientes pasos:

    Nos ajustamos dentro de la carpeta main del proyecto.
    comando: source myvenv/bin/activate
    comando: pip install -r requirements.txt
    comando: python manage.py makemigrations
    comando: python manage.py migrate
    comando: python manage.py runserver (corre por defecto en el 8000)

Luego dentro de angular haremos lo siguiente pasos:

    Nos ajustamos dentro de la carpeta raiz del proyecto.
    verificar si tenemos el Node Package Manager con comando:
        node -v
        npm -v
        Si no lo tenemos los descargamos.
    comando: npm install
    verificar que angular CLI esta instalado con comando:
        ng version
        si no esta instalado lo instalamos con comando:
            npm install -g @angular/cli -comando: ng serve (esto inicia por defecto el proyecto en 4200)

Todas las configuraciones que tienen por defecto sobre los puertos so# Aulora_Fronted

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

¡Eso es todo! Aulora estará corriendo localmente usando las imágenes Docker públicas de [carlospereafiguera](https://hub.docker.com/u/carlospereafiguera)

------------------------------------------------------------------------------------------------------------------------------------------------------------------

Para obtener los archivos del proyecto y poder programarlos a tu manera, puedes descargarte los repositorios o clonarlos y hacer lo siguiente: 

Paso 1: Clonar los repositorios:

Nos iremos a github y dentro de el, nos vamos al proyecto los cuales son los siguientes: 

Frontend: https://github.com/kowbalsqui/Aulora_Fronted.git
Bakend: https://github.com/kowbalsqui/Aulora_Bakend.git

Nos vamos al apartado donde dice "code" y le damos a ssh.

Le damos a una terminal e ingresamos el siguiente comando:

- git clone "ssh del codigo del proyecto"

Una vez los tenemos los dos, deberemos de meternos en el bakend y haremos los siguientes pasos: 

- Nos ajustamos dentro de la carpeta main del proyecto.
- comando: source myvenv/bin/activate
- comando: pip install -r requirements.txt
- comando: python manage.py makemigrations
- comando: python manage.py migrate
- comando: python manage.py runserver (corre por defecto en el 8000)

Luego dentro de angular haremos lo siguiente pasos: 

- Nos ajustamos dentro de la carpeta raiz del proyecto.
- verificar si tenemos el Node Package Manager con comando:
    - node -v
    - npm -v
    - Si no lo tenemos los descargamos.
- comando: npm install
- verificar que angular CLI esta instalado con comando:
    - ng version
    - si no esta instalado lo instalamos con comando:
        - npm install -g @angular/cli
-comando: ng serve (esto inicia por defecto el proyecto en 4200)

Todas las configuraciones que tienen por defecto sobre los puertos son las que estan predefinidas, si se quieren cambiar deberear de cambiar las cosas de comunicaciones tanto frontend como bakend. 
