# Servidor MCP - Un Backend para Agentes de IA
![Versión](https://img.shields.io/badge/version-4.0%20(Portable)-blue) ![Licencia](https://img.shields.io/badge/license-MIT-green)

Este proyecto es un **Servidor de Contexto y Orquestación de Git (MCP Server)**, diseñado para actuar como un backend inteligente para agentes de IA como [Goose](https://github.com/block/goose). Permite a un agente de IA interactuar con repositorios de GitHub de una manera estructurada, segura y profesional, siguiendo las mejores prácticas de desarrollo de software.

Fue desarrollado como parte de una sesión de programación colaborativa con un asistente de IA, evolucionando desde un simple script a un servicio contenedorizado y con estado.

---
## ✨ Características

* **Gestión de Contexto:** Carga y mantiene el contexto de un repositorio de Git, actualizándolo desde el remoto.
* **Flujo de Trabajo Profesional:** Habilita un flujo de trabajo basado en *feature branches* y Pull Requests.
* **Control Granular de Ramas:** Endpoints dedicados para crear y cambiar entre ramas de forma segura.
* **Orquestación de Git:** Automatiza la secuencia `add`, `commit`, y `push` a ramas específicas.
* **Integración con la API de GitHub:** Capacidad para crear repositorios y Pull Requests directamente.
* **Portable y Distribuible:** Contenerizado con Docker para una fácil instalación y ejecución en cualquier máquina.

---
## 🏛️ Filosofía de Arquitectura

Este sistema está diseñado bajo un principio de **Separación de Responsabilidades**:

* **El Agente de IA (Goose):** Actúa como el **Programador**. Su trabajo es generar y editar el contenido de los archivos de código.
* **El Servidor MCP:** Actúa como el **Ingeniero de DevOps**. Su trabajo es tomar el código que ya existe en el disco, gestionar el estado del repositorio con `git` y orquestar la comunicación con `GitHub`.

---
## 🚀 Cómo Empezar

### Prerrequisitos
* Tener [Docker](https://www.docker.com/get-started/) instalado y corriendo en tu máquina.
* Tener una cuenta de [GitHub](https://github.com/) y un [Token de Acceso Personal (PAT)](https://github.com/settings/tokens) con permisos de `repo` y `workflow`.

### Instalación y Ejecución

1.  **Clona el repositorio:**
    ```bash
    git clone [https://github.com/cupitatiana/mcp_server_github.git](https://github.com/cupitatiana/mcp_server_github.git)
    cd mcp_server_github
    ```

2.  **Crea el directorio de trabajo:**
    Este directorio será compartido con el contenedor de Docker para que los repositorios clonados sean persistentes.
    ```bash
    mkdir workspaces
    ```

3.  **Configura tu entorno personal (`.env`):**
    Crea un archivo llamado `.env` en la raíz del proyecto. Este archivo contendrá tus secretos y tu identidad. **¡Nunca subas este archivo a Git!**
    ```bash
    # Crea el archivo
    nano .env
    ```
    Pega el siguiente contenido y rellénalo con **TUS PROPIOS DATOS**:
    ```ini
    # Tu Token de Acceso Personal de GitHub
    GITHUB_TOKEN="ghp_tu_token_aqui"

    # Tu identidad para los commits de Git
    GIT_AUTHOR_NAME="tu-nombre-de-usuario"
    GIT_AUTHOR_EMAIL="tu-email@ejemplo.com"
    GIT_COMMITTER_NAME="tu-nombre-de-usuario"
    GIT_COMMITTER_EMAIL="tu-email@ejemplo.com"
    ```

4.  **Construye la imagen de Docker:**
    Este comando leerá el `Dockerfile` y empaquetará la aplicación.
    ```bash
    docker build -t mcp-server:latest .
    ```

5.  **Ejecuta el contenedor:**
    Este comando iniciará el servidor de forma persistente y conectará tu carpeta `workspaces` local con la del contenedor.
    ```bash
    docker run -d -p 8000:8000 --env-file .env --restart always -v "$(pwd)/workspaces":/app/workspaces --name mcp-server-container mcp-server:latest
    ```

6.  **¡Verifica que funciona!**
    Abre tu navegador y ve a `http://127.0.0.1:8000`. Deberías ver el mensaje de bienvenida. La documentación interactiva de la API está en **`http://127.0.0.1:8000/docs`**.

---
## ⚙️ Ejemplo de Flujo de Trabajo Completo

Puedes interactuar con el servidor usando cualquier cliente HTTP. Aquí tienes un ejemplo de la secuencia completa para crear una nueva funcionalidad:

```bash
# 1. Cargar el contexto de un repositorio existente
curl -X POST -H "Content-Type: application/json" -d '{"repo_url": "[https://github.com/cupitatiana/gooseAiTest](https://github.com/cupitatiana/gooseAiTest)"}' [http://127.0.0.1:8000/context/load_github_repo](http://127.0.0.1:8000/context/load_github_repo)

# 2. Crear una nueva rama para la funcionalidad
curl -X POST -H "Content-Type: application/json" -d '{"branch_name": "feat/add-new-feature"}' [http://127.0.0.1:8000/actions/create_and_switch_branch](http://127.0.0.1:8000/actions/create_and_switch_branch)

# (En este punto, un agente como Goose modificaría los archivos en la carpeta workspaces/gooseAiTest)

# 3. Hacer commit y push de los cambios a la nueva rama
curl -X POST -H "Content-Type: application/json" -d '{"commit_message": "feat: Implement the new feature"}' [http://127.0.0.1:8000/actions/commit_and_push_to_branch](http://127.0.0.1:8000/actions/commit_and_push_to_branch)

# 4. Crear el Pull Request para revisión
curl -X POST -H "Content-Type: application/json" -d '{"title": "Implement New Feature", "body": "Este PR añade la nueva funcionalidad Z.", "head_branch": "feat/add-new-feature"}' [http://127.0.0.1:8000/actions/create_pull_request](http://127.0.0.1:8000/actions/create_pull_request)
```

---
## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.