# 📦 Enterprise Logistics & Auth REST API (Python, Flask, Docker)

![Build Status](https://github.com/tu-usuario/flask-rbac-api/actions/workflows/ci.yml/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

API RESTful de nivel empresarial para **Gestión de Autenticación, RBAC y Logística de Envíos en Tiempo Real**.

🌐 **Swagger UI Live Demo**: [https://tu-servicio.onrender.com/apidocs](https://tu-servicio.onrender.com/apidocs)

---

## 🛠️ Tecnologías y Arquitectura

- **Backend**: Python 3.11, Flask, Flask-SQLAlchemy, Marshmallow, Gunicorn
- **Seguridad**: JWT (HS256), RBAC (Roles: `USER`, `DRIVER`, `ADMIN`), Werkzeug Password Hashing
- **Protección & Caché**: Flask-Limiter (`429 Rate Limit`), Redis Blacklist para Logout
- **Base de Datos**: PostgreSQL 15 (Producción), SQLite (Testing/Dev)
- **Infraestructura**: Docker, Docker Compose, GitHub Actions (CI/CD), Render

---

## 📡 Endpoints Principales

| Módulo | Método | Ruta | Descripción | Acceso |
|---|---|---|---|---|
| **Auth** | `POST` | `/api/auth/register` | Registro de usuarios | Público |
| **Auth** | `POST` | `/api/auth/login` | Login y emisión JWT | Público |
| **Auth** | `POST` | `/api/auth/logout` | Revocación token en Redis | Bearer Token |
| **Logística** | `POST` | `/api/shipments/` | Crear envío (Guía `TRK-...`) | Bearer Token |
| **Logística** | `GET` | `/api/shipments/` | Listar envíos | Bearer Token |
| **Logística** | `GET` | `/api/shipments/{trk}` | Rastreo público | Público |
| **Logística** | `POST` | `/api/shipments/{trk}/events` | Actualizar estado/ubicación | `DRIVER` / `ADMIN` |

---

## 🚀 Ejecución con Docker

```bash
cp .env.example .env
docker compose up --build