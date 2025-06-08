from flask import Flask, render_template, redirect, url_for
import docker

app = Flask(__name__)
client = docker.from_env()

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
    app.run(host='0.0.0.0', port=5000, debug=True)