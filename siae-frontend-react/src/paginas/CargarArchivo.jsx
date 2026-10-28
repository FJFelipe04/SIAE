import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Alerta from "../componentes/Alerta.jsx";
import TablaVista from "../componentes/TablaVista.jsx";
import { useSesion } from "../servicios/sesion.jsx";

export default function CargarArchivo() {
  const { api } = useSesion();
  const navegar = useNavigate();
  const [archivo, setArchivo] = useState(null);
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  async function subir(seleccionado) {
    if (!seleccionado) return;
    setError("");
    setCargando(true);
    try {
      setArchivo(await api("/archivos", { metodo: "POST", archivo: seleccionado }));
    } catch (e) {
      setArchivo(null);
      setError(e.message);
    } finally {
      setCargando(false);
    }
  }

  async function continuar() {
    const sesion = await api(`/sesiones?archivo_id=${archivo.id}`, { metodo: "POST" });
    navegar(`/transformar/${sesion.id}`);
  }

  return (
    <div className="container">
      <h1 className="h3">Cargar archivo de ventas</h1>
      <div className="zona-carga my-3" onDragOver={(e) => e.preventDefault()} onDrop={(e) => { e.preventDefault(); subir(e.dataTransfer.files[0]); }}>
        <p className="fs-5 mb-2">⬆ Arrastra aquí tu archivo o</p>
        <label className="btn btn-siae" htmlFor="archivo">Buscar en mi equipo</label>
        <input id="archivo" type="file" className="visually-hidden" accept=".xlsx,.csv" onChange={(e) => subir(e.target.files[0])} />
        <p className="small text-muted mt-2 mb-0">Formatos: .xlsx o .csv · Máximo 50 MB · Hasta 500.000 registros</p>
      </div>
      {cargando && <p>Cargando archivo…</p>}
      <Alerta>{error}</Alerta>
      {archivo && (
        <>
          <Alerta tipo="success"><b>{archivo.nombre_original}</b> cargado: {archivo.cantidad_registros} filas y {archivo.columnas.length} columnas.</Alerta>
          <h2 className="h5">Vista previa (datos originales, sin cambios)</h2>
          <TablaVista vista={archivo.vista_previa} />
          <button className="btn btn-siae me-2" onClick={continuar}>Continuar a transformar →</button>
          <button className="btn btn-outline-secondary" onClick={() => setArchivo(null)}>Cancelar</button>
        </>
      )}
    </div>
  );
}
