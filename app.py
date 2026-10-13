import logging
import os
import secrets
import time

import docker
from dotenv import load_dotenv
from flask import Flask, Response, abort, redirect, render_template, request, session, url_for

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("docker-web-manager")

app = Flask(__name__)
app.secret_key = os.environ.get("DWM_SECRET", secrets.token_hex(32))

try:
    client = docker.from_env()
    client.ping()
except Exception as e:
    log.critical("No se pudo conectar al daemon de Docker: %s", e)
    raise RuntimeError(f"Docker daemon no disponible: {e}") from e

DWM_USER = os.environ.get("DWM_USER")
DWM_PASS = os.environ.get("DWM_PASS")
if not DWM_USER or not DWM_PASS:
    raise RuntimeError("DWM_USER and DWM_PASS must be set in environment or .env file")


_rate_limit_store: dict[str, list[float]] = {}
RATE_LIMIT_MAX = int(os.environ.get("DWM_RATE_LIMIT", "30"))
RATE_WINDOW = 60


def generate_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]


app.jinja_env.globals["csrf_token"] = generate_csrf_token


def check_auth(username: str, password: str) -> bool:
    return username == DWM_USER and password == DWM_PASS


def authenticate():
    return Response("Login required", 401, {"WWW-Authenticate": 'Basic realm="Docker Manager"'})


def check_rate_limit(action: str = "default"):
    ip = request.remote_addr or "unknown"
    key = f"{ip}:{action}"
    now = time.time()
    window_start = now - RATE_WINDOW
    timestamps = _rate_limit_store.get(key, [])
    timestamps = [t for t in timestamps if t > window_start]
    if len(timestamps) >= RATE_LIMIT_MAX:
        log.warning("Rate limit reached for %s (%s)", ip, action)
        abort(429)
    timestamps.append(now)
    _rate_limit_store[key] = timestamps


@app.before_request
def require_auth():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        log.warning("Intento de login fallido desde %s", request.remote_addr)
        return authenticate()


@app.before_request
def csrf_protect():
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        token = request.form.get("_csrf_token", "")
        if not token or token != session.get("_csrf_token", ""):
            log.warning("CSRF token invalido desde %s", request.remote_addr)
            abort(403)


def log_action(action: str, container_name: str):
    log.info(
        "user=%s ip=%s action=%s container=%s",
        DWM_USER,
        request.remote_addr,
        action,
        container_name,
    )


def handle_docker_error(func_name: str, container_id: str):
    """Wrapper que maneja excepciones comunes de Docker."""
    try:
        c = client.containers.get(container_id)
        return c
    except docker.errors.NotFound:
        log.error("%s: contenedor %s no encontrado", func_name, container_id)
        abort(404)
    except docker.errors.APIError as e:
        log.error("%s: error API Docker: %s", func_name, e)
        abort(500, description=f"Error de Docker: {e}")
    except Exception as e:
        log.error("%s: error inesperado: %s", func_name, e)
        abort(500, description=str(e))


@app.route("/")
def index():
    try:
        containers = client.containers.list(all=True)
    except Exception as e:
        log.error("Error al listar contenedores: %s", e)
        abort(500, description="No se pudieron listar los contenedores")
    return render_template("index.html", containers=containers)


@app.route("/restart/<container_id>", methods=["POST"])
def restart(container_id):
    check_rate_limit("restart")
    c = handle_docker_error("restart", container_id)
    c.restart()
    log_action("restart", c.name)
    return redirect(url_for("index"))


@app.route("/stop/<container_id>", methods=["POST"])
def stop(container_id):
    check_rate_limit("stop")
    c = handle_docker_error("stop", container_id)
    c.stop()
    log_action("stop", c.name)
    return redirect(url_for("index"))


@app.route("/remove/<container_id>", methods=["POST"])
def remove(container_id):
    check_rate_limit("remove")
    c = handle_docker_error("remove", container_id)
    c.remove(force=True)
    log_action("remove", c.name)
    return redirect(url_for("index"))


@app.route("/health")
def health():
    try:
        client.ping()
        return {"status": "ok", "docker": "connected"}
    except Exception as e:
        return {"status": "error", "docker": str(e)}, 500


if __name__ == "__main__":
    host = os.environ.get("DWM_HOST", "127.0.0.1")
    port = int(os.environ.get("DWM_PORT", "5000"))
    app.run(host=host, port=port, debug=False)
