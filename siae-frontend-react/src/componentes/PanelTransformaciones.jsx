import { useState } from "react";

const ACCIONES = [
  { tipo: "formato_fecha", texto: "Formato de fecha" },
  { tipo: "cambiar_tipo", texto: "Convertir a número", parametros: { tipo: "numero" } },
  { tipo: "renombrar_columna", texto: "Renombrar", pide: "nuevo", etiqueta: "Nuevo nombre" },
  { tipo: "quitar_caracteres", texto: "Quitar caracteres", pide: "caracteres", etiqueta: "Caracteres a quitar" },
  { tipo: "eliminar_columna", texto: "Eliminar columna" },
  { tipo: "quitar_duplicados", texto: "Quitar filas duplicadas", sinColumna: true },
];

/** Panel lateral: selección de columna y botones de transformación (patrón Command en el servidor). */
export default function PanelTransformaciones({ columnas, onAplicar, deshabilitado }) {
  const [columna, setColumna] = useState(columnas[0] || "");
  const [valorExtra, setValorExtra] = useState("");
  const [pendiente, setPendiente] = useState(null);

  function pulsar(accion) {
    if (accion.pide) {
      setPendiente(accion);
      return;
    }
    onAplicar({ tipo: accion.tipo, columna: accion.sinColumna ? null : columna, parametros: accion.parametros || {} });
  }

  function confirmarExtra(evento) {
    evento.preventDefault();
    onAplicar({ tipo: pendiente.tipo, columna, parametros: { [pendiente.pide]: valorExtra } });
    setPendiente(null);
    setValorExtra("");
  }

  const columnaActual = columnas.includes(columna) ? columna : columnas[0];
  return (
    <div className="card p-3">
      <h2 className="h6">Transformar</h2>
      <label htmlFor="colObjetivo" className="form-label small">Columna a transformar</label>
      <select id="colObjetivo" className="form-select form-select-sm mb-2" value={columnaActual} onChange={(e) => setColumna(e.target.value)}>
        {columnas.map((c) => <option key={c}>{c}</option>)}
      </select>
      <div className="d-grid gap-2">
        {ACCIONES.map((a) => (
          <button key={a.tipo} data-tipo={a.tipo} className="btn btn-outline-primary btn-sm" disabled={deshabilitado} onClick={() => { setColumna(columnaActual); pulsar(a); }}>{a.texto}</button>
        ))}
      </div>
      {pendiente && (
        <form className="mt-3" onSubmit={confirmarExtra}>
          <label htmlFor="valorExtra" className="form-label small">{pendiente.etiqueta}</label>
          <input id="valorExtra" className="form-control form-control-sm mb-2" value={valorExtra} onChange={(e) => setValorExtra(e.target.value)} required autoFocus />
          <button className="btn btn-siae btn-sm me-2" type="submit">Aplicar</button>
          <button className="btn btn-outline-secondary btn-sm" type="button" onClick={() => setPendiente(null)}>Cancelar</button>
        </form>
      )}
    </div>
  );
}
