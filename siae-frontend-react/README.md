# SIAE – Front-end en React

Interfaz web de SIAE construida con React 18 + Vite, React Router, Bootstrap 5 y Chart.js.

## Ejecutar
```bash
npm install
cp .env.example .env      # VITE_API_URL apunta a la API FastAPI
npm run dev               # http://localhost:5173
```
Requiere la API de `../siae-backend` en ejecución.

## Estructura
- `src/servicios/` cliente de la API (`api.js`) y contexto de sesión (`sesion.jsx`).
- `src/componentes/` componentes reutilizables: barra, alertas, tabla de vista previa, panel de transformaciones, indicadores, gráfico.
- `src/paginas/` una página por ruta: login, registro, cargar, transformar, tablas, reportes.
