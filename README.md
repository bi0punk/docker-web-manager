# docker-web-manager

Lightweight web-based Docker container manager. Provides a simple Flask UI to list, start, stop, restart, and remove Docker containers.

**Security:** HTTP Basic Authentication is enforced. Set credentials via environment variables.

## Stack

Python 3, Flask, Docker SDK (docker-py)

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file or export these variables:

| Variable | Default | Description |
|---|---|---|
| `DWM_USER` | `admin` | HTTP Basic Auth username |
| `DWM_PASS` | `changeme` | HTTP Basic Auth password |

## Usage

```bash
python app.py
```

Open `http://localhost:5000` in your browser and log in with your credentials.

## Security notes

- All endpoints require HTTP Basic Authentication
- Docker socket is exposed to the web app — restrict access to trusted networks only
- Change the default credentials (`admin`/`changeme`) before deploying

## License

MIT
