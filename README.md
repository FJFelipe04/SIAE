# SIAE – Sistema de Inteligencia Analítica Empresarial

Proyecto formativo de Juan Felipe Perdomo Muñoz – Tecnólogo en Análisis y Desarrollo de Software, SENA (ficha 3282766).

| Carpeta | Contenido | Tecnología |
|---|---|---|
| `siae-backend/` | API REST del proyecto (autenticación, carga, transformación, reportes, administración) | Python 3, FastAPI, SQLAlchemy, Pandas, PostgreSQL |
| `siae-frontend-react/` | Interfaz web | React 18, Vite, Bootstrap 5, Chart.js |
| `siae-java/` | Módulo de usuarios con JDBC (consola) | Java 21, JDBC, PostgreSQL |
| `siae-web/` | Módulo web de usuarios con Servlets y JSP | Jakarta Servlet 6, JSP, Tomcat 10 |
| `servicio-autenticacion/` | Caso de servicio web de registro e inicio de sesión | FastAPI, SQLite |
| `siae-movil-android/` | App Android que consume la API | Java, Android SDK |
| `despliegue/` | Contenedores, máquina virtual y respaldo/restauración | Docker, Bash, pg_dump |

## Perfiles de usuario

| Perfil | Qué puede hacer |
|---|---|
| Analista | Cargar, transformar y confirmar sus archivos; ver sus reportes |
| Jefe comercial | Lo mismo que el analista |
| **Administrador** | Control global: ver todos los usuarios, cambiar su perfil, activar o desactivar cuentas, abrir/exportar/eliminar las tablas de cualquier usuario y revisar la bitácora de auditoría (menú **Administración**) |

Nadie puede registrarse como administrador desde la web. El administrador se crea desde el servidor:

```bash
cd siae-backend
python -m app.crear_admin
```

El script pide el correo; si la cuenta ya existe la convierte en administrador, si no, pide nombre y contraseña (oculta).
En una base de datos creada antes de este cambio, ejecutar primero `sql/migraciones/001_rol_administrador.sql`.

Pruebas: `siae-backend` 42 pruebas (pytest, cobertura 96 %), `servicio-autenticacion` 7 pruebas, colecciones de Postman en `siae-backend/docs/` y `servicio-autenticacion/`. La integración continua está en `.github/workflows/calidad.yml`.
