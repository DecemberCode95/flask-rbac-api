# 🔐 Flask REST API - Authentication & Role-Based Access Control (RBAC)

Una API REST profesional desarrollada en **Python (Flask)**, autenticación con **JWT**, control de acceso basado en roles (**RBAC**), persistencia con **PostgreSQL**, contenedorización completa con **Docker / Docker Compose** e integración continua con **GitHub Actions**.

---

## 🚀 Características del Proyecto

- **Autenticación JWT segura**: Emisión de JSON Web Tokens con firma HS256 y expiración configurable.
- **Control de Acceso basado en Roles (RBAC)**: Decoradores personalizados `@token_required` y `@roles_required('ADMIN', ...)` para proteger rutas.
- **Seguridad en Contraseñas**: Hashing seguro mediante `werkzeug.security`.
- **Persistencia Múltiple**: Soporte para PostgreSQL en Docker y SQLite en desarrollo/pruebas.
- **Pruebas Automatizadas**: Suite completa con `pytest` y reporte de cobertura de código (`pytest-cov`).
- **Contenedores Optimizados**: `Dockerfile` con usuario no-root por seguridad y servidor de producción `Gunicorn`.
- **Pipeline de CI/CD**: Workflow de GitHub Actions que ejecuta pruebas y valida la construcción de la imagen Docker en cada commit/PR.

---

## 🛠️ Instalación y Ejecución Local

### Opción 1: Con Docker Compose (Recomendado)

1. **Clonar el repositorio**:
   ```bash
   git clone [https://github.com/tu-usuario/flask-rbac-api.git](https://github.com/tu-usuario/flask-rbac-api.git)
   cd flask-rbac-api