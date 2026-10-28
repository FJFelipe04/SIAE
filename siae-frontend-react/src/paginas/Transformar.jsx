import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Alerta from "../componentes/Alerta.jsx";
import PanelTransformaciones from "../componentes/PanelTransformaciones.jsx";
import TablaVista from "../componentes/TablaVista.jsx";
import { useSesion } from "../servicios/sesion.jsx";

/** Sugiere una columna según su nombre (por ejemplo "Valor" para el valor de venta). */
const sugerir = (columnas, patron) => columnas.find((c) => patron.test(c)) || columnas[0];

export default function Transformar() {
  const { sesionId } = useParams();
  const { api } = useSesion();
  const navegar = useNavigate();
  const [sesion, setSesion] = useState(null);
  const [error, setError] = useState("");
  const [confirmando, setConfirmando] = useState(false);
  const [nombreTabla, setNombreTabla] = useState("");
  const [colFecha, setColFecha] = useState("");
  const [colValor, setColValor] = useState("");

  useEffect(() => {
    api(`/sesiones/${sesionId}`).then(setSesion).catch((e) => setError(e.message));
  }, [sesionId]);

  const columnas = sesion?.vista_previa.columnas || [];
  useEffect(() => {
    if (!columnas.includes(colFecha)) setColFecha(sugerir(columnas, /fecha|date/i));
    if (!columnas.includes(colValor)) setColValor(sugerir(columnas, /valor|total|venta|monto/i));
  }, [columnas.join("|")]);

  async function ejecutar(promesa) {
    setError("");
    try {
      setSesion(await promesa);
    } catch (e) {
      setError(e.message);
    }
  }

  async function confirmar(evento) {
    evento.preventDefault();
    setError("");
    try {
      const tabla = await api(`/sesiones/${sesionId}/confirmar`, { metodo: "POST", cuerpo: { nombre_tabla: nombreTabla, columna_fecha: colFecha, columna_valor: colValor } });
      navegar("/tablas", { state: { nueva: tabla } });
    } catch (e) {
      setError(e.message);
    }
  }

  async function cancelar() {
    await api(`/sesiones/${sesionId}/cancelar`, { metodo: "POST" });
    navegar("/cargar");
  }

  if (!sesion) return <Alerta>{error}</Alerta>;
  const pendiente = sesion.estado === "pendiente";
  return (
    <div className="row g-3">
      <aside className="col-lg-3">
        <div className="card p-3 mb-3">
          <h2 className="h6">1. Identifica tus columnas</h2>
          <label htmlFor="colFecha" className="form-label small">Columna de fecha</label>
          <select id="colFecha" className="form-select form-select-sm mb-2" value={colFecha} onChange={(e) => setColFecha(e.target.value)}>{columnas.map((c) => <option key={c}>{c}</option>)}</select>
          <label htmlFor="colValor" className="form-label small">Columna de valor</label>
          <select id="colValor" className="form-select form-select-sm" value={colValor} onChange={(e) => setColValor(e.target.value)}>{columnas.map((c) => <option key={c}>{c}</option>)}</select>
        </div>
        <PanelTransformaciones columnas={columnas} deshabilitado={!pendiente} onAplicar={(paso) => ejecutar(api(`/sesiones/${sesionId}/pasos`, { metodo: "POST", cuerpo: paso }))} />
      </aside>
      <section className="col-lg-9">
        <div className="card p-3">
          <h1 className="h4">Transformar datos</h1>
          <p className="mb-1 small text-muted">Pasos pendientes de confirmar:</p>
          <div className="mb-2" id="pasos">
            {sesion.pasos.length ? sesion.pasos.map((p) => <span className="paso" key={p.orden}>{p.orden}. {p.tipo.replaceAll("_", " ")}{p.columna ? ` – ${p.columna}` : ""}</span>) : <span className="small text-muted">Aún no hay pasos.</span>}
          </div>
          <div><button id="deshacer" className="btn btn-outline-secondary btn-sm mb-2" disabled={!sesion.pasos.length || !pendiente} onClick={() => ejecutar(api(`/sesiones/${sesionId}/pasos/ultimo`, { metodo: "DELETE" }))}>↶ Deshacer último paso</button></div>
          <Alerta>{error}</Alerta>
          <Alerta tipo="warning">{sesion.vista_previa.aviso}</Alerta>
          <TablaVista vista={sesion.vista_previa} />
          <div className="alert alert-light border py-2 small">Los cambios solo se ven aquí. El archivo original no se modifica.</div>
          {!confirmando ? (
            <div className="d-flex gap-2">
              <button id="revisar" className="btn btn-siae" disabled={!pendiente} onClick={() => setConfirmando(true)}>Revisar y confirmar →</button>
              <button className="btn btn-outline-secondary" onClick={cancelar}>Cancelar</button>
            </div>
          ) : (
            <form className="border rounded p-3 bg-light" onSubmit={confirmar}>
              <p>Se aplicarán <b>{sesion.pasos.length}</b> transformaciones. Resultado: {sesion.vista_previa.total_filas} filas y {columnas.length} columnas. Fecha: <b>{colFecha}</b> · Valor: <b>{colValor}</b>.</p>
              <label htmlFor="nombreTabla" className="form-label">Nombre de la nueva tabla (letras, números, _ o -)</label>
              <input id="nombreTabla" className="form-control mb-2" value={nombreTabla} onChange={(e) => setNombreTabla(e.target.value)} pattern="[A-Za-z0-9_\-]{3,100}" required />
              <button className="btn btn-ok me-2" type="submit" id="guardar">Confirmar y guardar</button>
              <button className="btn btn-outline-secondary" type="button" onClick={() => setConfirmando(false)}>Volver a editar</button>
            </form>
          )}
        </div>
      </section>
    </div>
  );
}
