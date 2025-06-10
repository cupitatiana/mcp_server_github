# --- Etapa 1: Base ---
FROM python:3.11-slim

# --- Etapa 2: Configuración del Entorno ---
WORKDIR /app

# --- NUEVO PASO: Instalar dependencias del sistema (como Git) ---
# Primero actualizamos la lista de paquetes, luego instalamos git sin paquetes recomendados
# para mantener la imagen pequeña, y finalmente limpiamos la caché.
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# --- Etapa 3: Instalar Dependencias de Python ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Etapa 4: Copiar el Código de la Aplicación ---
COPY . .

# --- Etapa 5: Comando de Ejecución ---
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
