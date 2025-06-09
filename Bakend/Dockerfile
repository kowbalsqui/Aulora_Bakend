# Usa una imagen base oficial de Python
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de dependencias
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos del proyecto
COPY . .

# Expone el puerto por el que Django se ejecutará
EXPOSE 8000

# Comando por defecto para desarrollo local (sin collectstatic ni gunicorn)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
