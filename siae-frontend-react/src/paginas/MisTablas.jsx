import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import Alerta from "../componentes/Alerta.jsx";
import { useSesion } from "../servicios/sesion.jsx";

export default function MisTablas() {
  const { api } = useSesion();
  const { state } = useLocation();
  const [tablas, setTablas] = useState([]);
  const [error, setError] = useState("");
  const cargar = () => api("/tablas").then(setTablas).catch((e) => setError(e.message));
  useEffect(() => { cargar(); }, []);

  async function exportar(tabla) {
    const archivo = await api(`/tablas/${tabla.id}/excel`, { binario: true });
    const enlace = document.createElement("a");
    enlace.href = URL.createObjectURL(archivo);
    enlace.download = `${tabla.nombre}.xlsx`;
    enlace.click();
  }

  async function eliminar(tabla) {
    if (!window.confirm(`¿Eliminar la tabla ${tabla.nombre}?`)) return;
    await api(`/tablas/${tabla.id}`, { metodo: "DELETE" });
    cargar();
  }

  return (
    <div className="container">
      <h1 className="h3">Mis tablas transformadas</h1>
      {state?.nueva && <Alerta tipo="success">Tabla “{state.nueva.nombre}” creada con {state.nueva.filas} filas{state.nueva.filas_omitidas ? ` (${state.nueva.filas_omitidas} fila(s) omitidas por no tener fecha o valor válido)` : ""}.</Alerta>}
      <Alerta>{error}</Alerta>
      <div className="table-responsive">
        <table className="table bg-white align-middle" id="tablas">
          <thead><tr><th>Nombre</th><th>Filas</th><th>Columnas</th><th><span className="visually-hidden">Acciones</span></th></tr></thead>
          <tbody>
            {tablas.length === 0 && <tr><td colSpan="4" className="text-muted">Todavía no tienes tablas. <Link to="/cargar">Carga un archivo</Link>.</td></tr>}
            {tablas.map((t) => (
              <tr key={t.id}>
                <td>{t.nombre}</td><td>{t.filas}</td><td>{t.columnas}</td>
                <td className="text-nowrap">
                  <Link className="btn btn-sm btn-siae me-1" to={`/reportes?tabla=${t.id}`}>Reporte</Link>
                  <button className="btn btn-sm btn-outline-secondary me-1" onClick={() => exportar(t)}>Exportar Excel</button>
                  <button className="btn btn-sm btn-outline-danger" onClick={() => eliminar(t)}>Eliminar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
