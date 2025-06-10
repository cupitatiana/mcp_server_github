# Servidor MCP - Un Backend para Agentes de IA
![Versión](https://img.shields.io/badge/version-3.2-blue) ![Licencia](https://img.shields.io/badge/license-MIT-green)

Este proyecto es un **Servidor de Contexto y Orquestación de Git (MCP Server)**, diseñado para actuar como un backend inteligente para agentes de IA como [Goose](https://github.com/block/goose). Permite a un agente de IA interactuar con repositorios de GitHub de una manera estructurada, segura y profesional, siguiendo las mejores prácticas de desarrollo de software.

Fue desarrollado como parte de una sesión de programación colaborativa con un asistente de IA.

---
## ✨ Características

* **Gestión de Contexto:** Carga y mantiene el contexto de un repositorio de Git, actualizándolo desde el remoto.
* **Flujo de Trabajo Profesional:** Habilita un flujo de trabajo basado en *feature branches* y Pull Requests.
* **Control Granular de Ramas:** Endpoints dedicados para crear y cambiar entre ramas de forma segura.
* **Orquestación de Git:** Automatiza la secuencia `add`, `commit`, y `push` a ramas específicas.
* **Integración con la API de GitHub:** Capacidad para crear repositorios y Pull Requests directamente.
* **Listo para Despliegue:** Contenerizado con Docker para una fácil distribución y ejecución.

---
## 🚀 Cómo Empezar

### Prerrequisitos
* Tener [Docker](https://www.docker.com/get-started/) instalado y corriendo en tu máquina.
* Tener una cuenta de [GitHub](https://github.com/) y un [Token de Acceso Personal (PAT)](https://github.com/settings/tokens) con permisos de `repo` y `workflow`.

### Instalación y Ejecución

1.  **Clona este repositorio:**
    ```bash
    git clone [https://github.com/cupitatiana/mcp_server_github.git](https://github.com/cupitatiana/mcp_server_github.git)
    cd mcp-server
    ```

2.  **Crea tu archivo de entorno:**
    Copia el archivo de ejemplo `.env.example` (que deberás crear) a `.env` y edítalo con tu propio Token de Acceso Personal de GitHub.
    ```bash
    cp .env.example .env
    nano .env 
    # Dentro del archivo, pon: GITHUB_TOKEN="ghp_tu_token_aqui"
    ```

3.  **Construye la imagen de Docker:**
    Desde la raíz del proyecto, ejecuta:
    ```bash
    docker build -t mcp-server:latest .
    ```

4.  **Ejecuta el contenedor:**
    Este comando iniciará el servidor en segundo plano y lo reiniciará automáticamente.
    ```bash
    docker run -d -p 8000:8000 --env-file .env --restart always --name mcp-server-container mcp-server:latest
    ```
5.  **¡Verifica que funciona!**
    Abre tu navegador y ve a `http://127.0.0.1:8000`. Deberías ver el mensaje de bienvenida. La documentación interactiva de la API está en `http://127.0.0.1:8000/docs`.

---
## ⚙️ Uso de la API

Puedes interactuar con el servidor usando cualquier cliente HTTP, como `curl`. Aquí tienes un ejemplo de flujo de trabajo:

```bash
# 1. Cargar el contexto de un repositorio
curl -X POST -H "Content-Type: application/json" \
-d '{"repo_url": "[https://github.com/tu_usuario/tu_repo](https://github.com/tu_usuario/tu_repo)"}' \
[http://127.0.0.1:8000/context/load_github_repo](http://127.0.0.1:8000/context/load_github_repo)

# 2. Crear una nueva rama
curl -X POST -H "Content-Type: application/json" \
-d '{"branch_name": "feat/nueva-funcionalidad"}' \
[http://127.0.0.1:8000/actions/create_and_switch_branch](http://127.0.0.1:8000/actions/create_and_switch_branch)

# 3. Subir cambios (después de que un agente haya modificado los archivos localmente)
curl -X POST -H "Content-Type: application/json" \
-d '{"commit_message": "feat: Implementar nueva funcionalidad"}' \
[http://127.0.0.1:8000/actions/commit_and_push_to_branch](http://127.0.0.1:8000/actions/commit_and_push_to_branch)

# 4. Crear un Pull Request
curl -X POST -H "Content-Type: application/json" \
-d '{"title": "Implementar Nueva Funcionalidad", "body": "Este PR añade la nueva funcionalidad X.", "head_branch": "feat/nueva-funcionalidad"}' \
[http://127.0.0.1:8000/actions/create_pull_request](http://127.0.0.1:8000/actions/create_pull_request)
```

---
## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
