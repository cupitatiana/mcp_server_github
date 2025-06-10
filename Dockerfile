# --- Etapa 1: Base ---
FROM python:3.11-slim

# --- Etapa 2: Configuración del Entorno ---
WORKDIR /app

# --- Etapa 3: Instalar Dependencias del Sistema ---
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# --- Etapa 4: Configurar Git para que confíe en los directorios montados ---
RUN git config --global --add safe.directory '*'

# --- NUEVO PASO DE VERIFICACIÓN ---
# Imprime la configuración global de Git para que podamos verla en el log de build.
# ¡Aquí veremos si la línea anterior funcionó!
RUN git config --global --list

# --- Etapa 5: Instalar Dependencias de Python ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Etapa 6: Copiar el Código de la Aplicación ---
COPY . .

# --- Etapa 7: Comando de Ejecución ---
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]