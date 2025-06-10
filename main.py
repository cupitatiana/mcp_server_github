import os
import subprocess
import shutil
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import re
import requests

# --- Configuración Inicial ---
load_dotenv()
app = FastAPI(title="MCP Server v3.2 - Feature Complete") # <- Título actualizado
WORKSPACES_DIR = "workspaces"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# --- Base de Datos en Memoria ---
context_db = {
    "current_repo_url": None,
    "local_repo_path": None,
    "current_branch": None,
    "github_owner": None,
    "github_repo_name": None
}

# --- Modelos de Datos ---
class GithubRepo(BaseModel):
    repo_url: str

class BranchRequest(BaseModel):
    branch_name: str

class CommitRequest(BaseModel):
    commit_message: str

class PullRequestRequest(BaseModel):
    title: str
    body: str
    head_branch: str
    base_branch: str = "main"

# --- El modelo de datos CORRECTO para subir un proyecto ---
class UploadProjectRequest(BaseModel):
    project_dir_name: str # <- ¡Este es el campo correcto!
    repo_name: str
    is_private: bool = True

# --- Funciones de Ayuda (sin cambios) ---
def run_command(command, cwd):
    print(f"Ejecutando: '{' '.join(command)}' en '{cwd}'")
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        raise HTTPException(status_code=500, detail=result.stderr)
    print(f"OK: {result.stdout}")
    return result.stdout

# --- Endpoints de la API ---

@app.get("/")
def read_root():
    return {"message": "MCP Server v3.2 (con subida de proyectos restaurada) está activo."}

@app.get("/context/current")
def get_current_context():
    return {"context": context_db}

@app.post("/context/load_github_repo")
def load_github_context(repo: GithubRepo):
    # (Esta función se mantiene igual)
    if not GITHUB_TOKEN:
        raise HTTPException(status_code=500, detail="GITHUB_TOKEN no configurado.")
    match = re.search(r"github\.com/([^/]+)/([^/]+)", repo.repo_url)
    if not match:
        raise HTTPException(status_code=400, detail="URL de repositorio no válida.")
    owner, repo_name = match.group(1), match.group(2).replace('.git', '')
    local_path = os.path.join(WORKSPACES_DIR, repo_name)
    if os.path.exists(local_path):
        run_command(["git", "checkout", "main"], cwd=local_path)
        run_command(["git", "pull"], cwd=local_path)
    else:
        auth_repo_url = f"https://{GITHUB_TOKEN}@github.com/{owner}/{repo_name}.git"
        run_command(["git", "clone", auth_repo_url, local_path], cwd=".")
    context_db.update({"current_repo_url": repo.repo_url, "local_repo_path": local_path,"current_branch": "main", "github_owner": owner, "github_repo_name": repo_name})
    return {"message": f"Repositorio {repo.repo_url} listo y actualizado en la rama 'main'."}

@app.post("/actions/switch_branch")
def switch_branch(request: BranchRequest):
    # (Esta función se mantiene igual)
    local_repo_path = context_db.get("local_repo_path")
    if not local_repo_path:
        raise HTTPException(status_code=400, detail="Ningún repositorio en contexto.")
    run_command(["git", "checkout", request.branch_name], cwd=local_repo_path)
    context_db["current_branch"] = request.branch_name
    return {"message": f"Cambiado a la rama '{request.branch_name}'."}

@app.post("/actions/create_and_switch_branch")
def create_and_switch_branch(request: BranchRequest):
    # (Esta función se mantiene igual)
    local_repo_path = context_db.get("local_repo_path")
    if not local_repo_path:
        raise HTTPException(status_code=400, detail="Ningún repositorio en contexto.")
    run_command(["git", "checkout", "-b", request.branch_name], cwd=local_repo_path)
    context_db["current_branch"] = request.branch_name
    return {"message": f"Rama '{request.branch_name}' creada y seleccionada."}

@app.post("/actions/commit_and_push_to_branch")
def commit_and_push_to_branch(request: CommitRequest):
    # (Esta función se mantiene igual)
    local_repo_path = context_db.get("local_repo_path")
    current_branch = context_db.get("current_branch")
    if not local_repo_path or not current_branch:
        raise HTTPException(status_code=400, detail="Ningún repositorio o rama en contexto.")
    status_result = run_command(["git", "status", "--porcelain"], cwd=local_repo_path)
    if not status_result:
        return {"message": "No se detectaron cambios en el repositorio."}
    run_command(["git", "add", "."], cwd=local_repo_path)
    run_command(["git", "commit", "-m", request.commit_message], cwd=local_repo_path)
    run_command(["git", "push", "--set-upstream", "origin", current_branch], cwd=local_repo_path)
    return {"message": f"¡Éxito! Cambios subidos a la rama '{current_branch}'."}

@app.post("/actions/create_pull_request")
def create_pull_request(request: PullRequestRequest):
    # (Esta función se mantiene igual)
    owner = context_db.get("github_owner")
    repo_name = context_db.get("github_repo_name")
    if not owner or not repo_name:
        raise HTTPException(status_code=400, detail="Contexto de repositorio incompleto.")
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    data = {"title": request.title, "body": request.body, "head": request.head_branch, "base": request.base_branch}
    response = requests.post(api_url, json=data, headers=headers)
    if response.status_code not in [200, 201]:
        if response.status_code == 422:
             raise HTTPException(status_code=422, detail=f"No se pudo crear el PR. ¿Ya existe o no hay nuevos commits? Detalle: {response.text}")
        raise HTTPException(status_code=response.status_code, detail=f"Error al crear PR en GitHub: {response.text}")
    pr_data = response.json()
    return {"message": "¡Pull Request creado exitosamente!", "pr_url": pr_data["html_url"]}


# --- El endpoint modificado ---
@app.post("/actions/upload_project_to_new_repo")
def upload_project_to_new_repo(request: UploadProjectRequest):
    """
    Toma un proyecto que ya está en el directorio 'workspaces',
    crea un repo en GitHub y sube el código.
    """
    if not GITHUB_TOKEN:
        raise HTTPException(status_code=500, detail="GITHUB_TOKEN no configurado.")
    
    # --- LÓGICA MEJORADA ---
    # Ahora construimos la ruta completa DESDE DENTRO del punto de vista del servidor.
    local_path = os.path.join(WORKSPACES_DIR, request.project_dir_name)
    
    if not os.path.isdir(local_path):
        raise HTTPException(status_code=404, detail=f"El directorio del proyecto '{local_path}' no existe DENTRO del workspace del servidor.")

    # El resto de la lógica para crear el repo y hacer el push se mantiene igual,
    # ya que opera sobre la 'local_path' que hemos validado.
    
    print(f"Creando repositorio '{request.repo_name}' en GitHub...")
    api_url = "https://api.github.com/user/repos"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    data = {"name": request.repo_name, "private": request.is_private}
    response = requests.post(api_url, json=data, headers=headers)
    
    if response.status_code not in [200, 201]:
        raise HTTPException(status_code=response.status_code, detail=f"Error al crear repo en GitHub: {response.text}")
    
    repo_data = response.json()
    clone_url = repo_data["clone_url"]
    auth_clone_url = clone_url.replace("https://", f"https://{GITHUB_TOKEN}@")
    print(f"Repositorio creado exitosamente: {repo_data['html_url']}")

    run_command(["git", "init"], cwd=local_path)
    run_command(["git", "remote", "add", "origin", auth_clone_url], cwd=local_path)
    run_command(["git", "add", "."], cwd=local_path)
    run_command(["git", "commit", "-m", "Initial commit from MCP Server"], cwd=local_path)
    run_command(["git", "branch", "-M", "main"], cwd=local_path)
    run_command(["git", "push", "-u", "origin", "main"], cwd=local_path)
    
    return {
        "message": "¡Proyecto subido exitosamente a un nuevo repositorio de GitHub!",
        "repo_url": repo_data["html_url"]
    }