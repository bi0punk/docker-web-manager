from flask import Flask, render_template, redirect, url_for, request, Response
import docker
import os

app = Flask(__name__)
client = docker.from_env()

def check_auth(username, password):
    return username == os.getenv("DWM_USER", "admin") and password == os.getenv("DWM_PASS", "changeme")

def authenticate():
    return Response("Login required", 401, {"WWW-Authenticate": 'Basic realm="Docker Manager"'})

@app.before_request
def require_auth():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

@app.route('/')
def index():
    # Obtiene todos los contenedores
    containers = client.containers.list(all=True)
    return render_template('index.html', containers=containers)

@app.route('/restart/<container_id>')
def restart(container_id):
    c = client.containers.get(container_id)
    c.restart()
    return redirect(url_for('index'))

@app.route('/stop/<container_id>')
def stop(container_id):
    c = client.containers.get(container_id)
    c.stop()
    return redirect(url_for('index'))

@app.route('/remove/<container_id>')
def remove(container_id):
    c = client.containers.get(container_id)
    c.remove(force=True)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)