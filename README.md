# SIAE – Sistema de Inteligencia Analítica Empresarial

Proyecto formativo de Juan Felipe Perdomo Muñoz – Tecnólogo en Análisis y Desarrollo de Software, SENA (ficha 3282766).

| Carpeta | Contenido | Tecnología |
|---|---|---|
| `siae-backend/` | API REST del proyecto (autenticación, carga, transformación, reportes) | Python 3, FastAPI, SQLAlchemy, Pandas, PostgreSQL |
| `siae-frontend-react/` | Interfaz web | React 18, Vite, Bootstrap 5, Chart.js |
| `siae-java/` | Módulo de usuarios con JDBC (consola) | Java 21, JDBC, PostgreSQL |
| `siae-web/` | Módulo web de usuarios con Servlets y JSP | Jakarta Servlet 6, JSP, Tomcat 10 |
| `servicio-autenticacion/` | Caso de servicio web de registro e inicio de sesión | FastAPI, SQLite |

Pruebas: `siae-backend` 31 pruebas (pytest), `servicio-autenticacion` 7 pruebas, colecciones de Postman en `siae-backend/docs/` y `servicio-autenticacion/`.
