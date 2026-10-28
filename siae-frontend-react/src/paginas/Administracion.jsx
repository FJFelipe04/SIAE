import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Alerta from "../componentes/Alerta.jsx";
import { useSesion } from "../servicios/sesion.jsx";

const PERFILES = { analista: "Analista", jefe_comercial: "Jefe comercial", administrador: "Administrador" };
const fecha = (valor) => (valor ? new Date(valor).toLocaleString("es-CO") : "—");

/** Panel global del administrador: usuarios, tablas de todos y bitácora de auditoría. */
export default function Administracion() {
  const { api, correo } = useSesion();
  const [resumen, setResumen] = useState(null);
  const [usuarios, setUsuarios] = useState([]);
  const [tablas, setTablas] = useState([]);
  const [eventos, setEventos] = useState([]);
  const [error, setError] = useState("");
  const [aviso, setAviso] = useState("");

  async function cargar() {
    try {
      const [r, u, t, e] = await Promise.all([api("/admin/resumen"), api("/admin/usuarios"), api("/admin/tablas"), api("/admin/auditoria?limite=50")]);
      setResumen(r); setUsuarios(u); setTablas(t); setEventos(e);
    } catch (e) {
      setError(e.message);
    }
  }
  useEffect(() => { cargar(); }, []);

  async function cambiar(usuario, cambio, mensaje) {
    setError(""); setAviso("");
    try {
      await api(`/admin/usuarios/${usuario.id}`, { metodo: "PATCH", cuerpo: cambio });
      setAviso(mensaje);
      cargar();
    } catch (e) {
      setError(e.message);
    }
  }

  async function exportar(tabla) {
    const archivo = await api(`/tablas/${tabla.id}/excel`, { binario: true });
    const enlace = document.createElement("a");
    enlace.href = URL.createObjectURL(archivo);
    enlace.download = `${tabla.nombre}.xlsx`;
    enlace.click();
  }

  async function eliminar(tabla) {
    if (!window.confirm(`¿Eliminar la tabla ${tabla.nombre} de ${tabla.propietario}?`)) return;
    await api(`/tablas/${tabla.id}`, { metodo: "DELETE" });
    setAviso(`Tabla ${tabla.nombre} eliminada.`);
    cargar();
  }

  return (
    <div className="container">
      <h1 className="h3">Administración</h1>
      <p className="text-muted">Control global de SIAE: usuarios, tablas de todos y registro de actividad.</p>
      <Alerta>{error}</Alerta>
      <Alerta tipo="success">{aviso}</Alerta>

      {resumen && (
        <div className="row g-3 mb-4" id="resumen">
          {[["Usuarios", resumen.usuarios], ["Activos", resumen.usuarios_activos], ["Administradores", resumen.administradores], ["Archivos", resumen.archivos], ["Tablas", resumen.tablas], ["Registros de venta", resumen.registros.toLocaleString("es-CO")]].map(([nombre, valor]) => (
            <div className="col-6 col-md-2" key={nombre}><div className="card p-3 text-center"><div className="kpi">{valor}</div><div className="small text-muted">{nombre}</div></div></div>
          ))}
        </div>
      )}

      <h2 className="h5">Usuarios</h2>
      <div className="table-responsive mb-4">
        <table className="table bg-white align-middle" id="usuarios">
          <thead><tr><th>Nombre</th><th>Correo</th><th>Perfil</th><th>Estado</th><th>Archivos</th><th>Tablas</th><th>Último acceso</th><th><span className="visually-hidden">Acciones</span></th></tr></thead>
          <tbody>
            {usuarios.map((u) => {
              const soyYo = u.correo === correo;
              return (
                <tr key={u.id} data-correo={u.correo}>
                  <td>{u.nombre}{soyYo && <span className="badge bg-secondary ms-1">Tú</span>}</td>
                  <td>{u.correo}</td>
                  <td>
                    <label className="visually-hidden" htmlFor={`perfil-${u.id}`}>Perfil de {u.nombre}</label>
                    <select id={`perfil-${u.id}`} className="form-select form-select-sm" style={{ minWidth: "10rem" }} value={u.perfil} disabled={soyYo}
                      onChange={(e) => cambiar(u, { perfil: e.target.value }, `${u.nombre} ahora es ${PERFILES[e.target.value]}.`)}>
                      {Object.entries(PERFILES).map(([valor, texto]) => <option key={valor} value={valor}>{texto}</option>)}
                    </select>
                  </td>
                  <td>{u.activo ? <span className="badge bg-success">Activo</span> : <span className="badge bg-danger">Desactivado</span>}</td>
                  <td>{u.archivos}</td><td>{u.tablas}</td><td className="small">{fecha(u.ultimo_acceso)}</td>
                  <td>
                    {!soyYo && (u.activo
                      ? <button className="btn btn-sm btn-outline-danger" onClick={() => cambiar(u, { activo: false }, `Cuenta de ${u.nombre} desactivada.`)}>Desactivar</button>
                      : <button className="btn btn-sm btn-ok" onClick={() => cambiar(u, { activo: true }, `Cuenta de ${u.nombre} activada.`)}>Activar</button>)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <h2 className="h5">Tablas de todos los usuarios</h2>
      <div className="table-responsive mb-4">
        <table className="table bg-white align-middle" id="tablasGlobales">
          <thead><tr><th>Tabla</th><th>Propietario</th><th>Filas</th><th>Creada</th><th><span className="visually-hidden">Acciones</span></th></tr></thead>
          <tbody>
            {tablas.length === 0 && <tr><td colSpan="5" className="text-muted">Nadie ha confirmado tablas todavía.</td></tr>}
            {tablas.map((t) => (
              <tr key={t.id}>
                <td>{t.nombre}</td><td>{t.propietario}<div className="small text-muted">{t.correo_propietario}</div></td>
                <td>{t.filas.toLocaleString("es-CO")}</td><td className="small">{fecha(t.creada_en)}</td>
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

      <h2 className="h5">Actividad reciente</h2>
      <div className="table-responsive">
        <table className="table table-sm bg-white small" id="bitacora">
          <thead><tr><th>Fecha</th><th>Acción</th><th>Usuario</th><th>Detalle</th></tr></thead>
          <tbody>{eventos.map((e) => <tr key={e.id}><td>{fecha(e.fecha)}</td><td>{e.accion}</td><td>{e.correo || "—"}</td><td>{e.detalle || ""}</td></tr>)}</tbody>
        </table>
      </div>
    </div>
  );
}
