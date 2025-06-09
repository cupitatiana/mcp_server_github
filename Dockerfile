# Usamos una imagen oficial y ligera de Python como base. Es nuestro "sistema operativo".
FROM python:3.11-slim

# Establecemos un directorio de trabajo dentro del contenedor para mantener todo ordenado.
WORKDIR /app

# Copiamos SOLO el archivo de requisitos primero.
# Esto es un truco de optimización: si no cambiamos las dependencias,
# Docker reutilizará la capa ya instalada, haciendo las futuras construcciones mucho más rápidas.
COPY requirements.txt .

# Instalamos las dependencias de Python que definimos en requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

# Ahora copiamos el resto del código de nuestra aplicación al contenedor.
COPY . .

# El comando que se ejecutará cuando el contenedor se inicie.
# Le dice a Uvicorn que inicie nuestra app 'app' desde el archivo 'main.py'
# y que escuche en todas las interfaces de red ('0.0.0.0') en el puerto 8000.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
