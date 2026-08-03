# docker-web-manager

Lightweight web-based Docker container manager. Provides a simple Flask UI to list, start, stop, restart, and remove Docker containers.

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![CI](https://github.com/bi0punk/docker-web-manager/actions/workflows/ci.yml/badge.svg)](https://github.com/bi0punk/docker-web-manager/actions/workflows/ci.yml)

## Tabla de Contenidos

- [Características](#características)
- [Stack](#stack)
- [Arquitectura](#arquitectura)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Tests](#tests)
- [Configuración](#configuración)
- [CI](#ci)
- [Seguridad](#seguridad)
- [Limitaciones / Roadmap](#limitaciones--roadmap)
- [Licencia](#licencia)

## Características

- Listado completo de contenedores (running + stopped)
- Acciones: stop, restart, remove containers
- Interfaz web limpia con Bootstrap
- Autenticación HTTP Basic
- Protección CSRF en todos los formularios POST
- Rate limiting por IP en endpoints críticos
- Logging de operaciones (login, stop, restart, remove)
- Health check endpoint (`/health`)
- Conexión al socket Docker local

## Stack

- Python 3.11+, Flask, Docker SDK for Python (docker-py)

## Arquitectura

```
docker-web-manager/
├── app.py
├── templates/
│   └── index.html
├── tests/
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

## Requisitos

- Python 3.11+
- Docker Engine (socket `/var/run/docker.sock`)
- El usuario que ejecuta la app debe tener permisos sobre el socket Docker

## Instalación

```bash
git clone https://github.com/bi0punk/docker-web-manager.git
cd docker-web-manager
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Uso

```bash
python app.py
```

Abrir `http://localhost:5000` e iniciar sesión con las credenciales configuradas. La interfaz muestra todos los contenedores con botones para gestionarlos.

## Tests

```bash
pip install pytest ruff
pytest -q
ruff check .
```

## Configuración

Variables de entorno (ver `.env.example`):

| Variable | Default | Descripción |
|---|---|---|
| `DWM_USER` | (requerido) | Usuario HTTP Basic Auth |
| `DWM_PASS` | (requerido) | Contraseña HTTP Basic Auth |
| `DWM_SECRET` | (generada) | Secret key de Flask para sesiones/CSRF |
| `DWM_HOST` | `127.0.0.1` | Host de escucha |
| `DWM_PORT` | `5000` | Puerto |
| `DWM_RATE_LIMIT` | `30` | Peticiones máximas por minuto por IP |

## CI

GitHub Actions ejecuta ruff lint + pytest en cada push y PR.

## Seguridad

- HTTP Basic Authentication en todos los endpoints
- Protección CSRF con tokens de sesión en formularios POST
- Rate limiting (30 req/min por IP)
- Logging de eventos de seguridad (login, operaciones críticas)
- El socket Docker se expone a la web — restringir acceso a redes de confianza
- Cambiar credenciales antes de desplegar
- Ejecutar detrás de un reverse proxy con HTTPS en producción

## Limitaciones / Roadmap

- [ ] Soporte para Docker Compose (up/down stacks)
- [ ] Logs en vivo por contenedor via WebSocket
- [ ] Estadísticas de uso (CPU, memoria, red)
- [ ] Manejo de imágenes (pull, build, remove)

## Licencia

MIT
