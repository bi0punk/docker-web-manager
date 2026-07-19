import os
import secrets
from flask import Flask, render_template, redirect, url_for, request, Response, abort
import docker
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("DWM_SECRET", secrets.token_hex(32))
client = docker.from_env()

DWM_USER = os.environ.get("DWM_USER")
DWM_PASS = os.environ.get("DWM_PASS")
if not DWM_USER or not DWM_PASS:
    raise RuntimeError("DWM_USER and DWM_PASS must be set in environment or .env file")

def check_auth(username, password):
    return username == DWM_USER and password == DWM_PASS

def authenticate():
    return Response("Login required", 401, {"WWW-Authenticate": 'Basic realm="Docker Manager"'})

@app.before_request
def require_auth():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

@app.route('/')
def index():
    containers = client.containers.list(all=True)
    return render_template('index.html', containers=containers)

@app.route('/restart/<container_id>', methods=['POST'])
def restart(container_id):
    try:
        c = client.containers.get(container_id)
        c.restart()
    except docker.errors.NotFound:
        abort(404)
    return redirect(url_for('index'))

@app.route('/stop/<container_id>', methods=['POST'])
def stop(container_id):
    try:
        c = client.containers.get(container_id)
        c.stop()
    except docker.errors.NotFound:
        abort(404)
    return redirect(url_for('index'))

@app.route('/remove/<container_id>', methods=['POST'])
def remove(container_id):
    try:
        c = client.containers.get(container_id)
        c.remove(force=True)
    except docker.errors.NotFound:
        abort(404)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
