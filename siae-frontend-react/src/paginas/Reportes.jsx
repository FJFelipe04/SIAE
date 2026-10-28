import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import Alerta from "../componentes/Alerta.jsx";
import GraficoVentas from "../componentes/GraficoVentas.jsx";
import Indicadores from "../componentes/Indicadores.jsx";
import { useSesion } from "../servicios/sesion.jsx";

export default function Reportes() {
  const { api } = useSesion();
  const [parametros] = useSearchParams();
  const [tablas, setTablas] = useState([]);
  const [filtro, setFiltro] = useState({ tabla_id: parametros.get("tabla") || "", tipo: "lineas", agrupacion: "mes", fecha_inicio: "", fecha_fin: "" });
  const [reporte, setReporte] = useState(null);
  const [error, setError] = useState("");
  const cambiar = (campo) => (e) => setFiltro({ ...filtro, [campo]: e.target.value });

  useEffect(() => {
    api("/tablas").then((lista) => {
      setTablas(lista);
      if (!filtro.tabla_id && lista.length) setFiltro((f) => ({ ...f, tabla_id: String(lista[0].id) }));
    });
  }, []);

  async function generar(evento) {
    evento?.preventDefault();
    setError("");
    try {
      const cuerpo = { ...filtro, tabla_id: Number(filtro.tabla_id), fecha_inicio: filtro.fecha_inicio || null, fecha_fin: filtro.fecha_fin || null };
      setReporte(await api("/reportes", { metodo: "POST", cuerpo }));
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => { if (filtro.tabla_id) generar(); }, [filtro.tabla_id]);

  if (!tablas.length) return <div className="container"><h1 className="h3">Reporte de ventas</h1><Alerta tipo="info">No hay tablas confirmadas todavía.</Alerta></div>;
  return (
    <div className="container">
      <h1 className="h3">Reporte de ventas</h1>
      <form className="row g-2 align-items-end mb-2" onSubmit={generar}>
        <div className="col-sm-3"><label htmlFor="tabla" className="form-label">Tabla</label><select id="tabla" className="form-select" value={filtro.tabla_id} onChange={cambiar("tabla_id")}>{tablas.map((t) => <option key={t.id} value={t.id}>{t.nombre}</option>)}</select></div>
        <div className="col-6 col-sm-2"><label htmlFor="desde" className="form-label">Desde</label><input id="desde" type="date" className="form-control" value={filtro.fecha_inicio} onChange={cambiar("fecha_inicio")} /></div>
        <div className="col-6 col-sm-2"><label htmlFor="hasta" className="form-label">Hasta</label><input id="hasta" type="date" className="form-control" value={filtro.fecha_fin} onChange={cambiar("fecha_fin")} /></div>
        <div className="col-6 col-sm-2"><label htmlFor="agrupacion" className="form-label">Agrupar por</label><select id="agrupacion" className="form-select" value={filtro.agrupacion} onChange={cambiar("agrupacion")}><option value="dia">Día</option><option value="mes">Mes</option><option value="anio">Año</option></select></div>
        <div className="col-6 col-sm-2"><label htmlFor="tipo" className="form-label">Gráfico</label><select id="tipo" className="form-select" value={filtro.tipo} onChange={cambiar("tipo")}><option value="lineas">Líneas</option><option value="barras">Barras</option><option value="torta">Torta</option></select></div>
        <div className="col-sm-1"><button id="aplicar" className="btn btn-siae w-100" type="submit">Aplicar</button></div>
      </form>
      <Alerta>{error}</Alerta>
      {reporte && (<><Indicadores indicadores={reporte.indicadores} /><div className="card p-3"><h2 className="h6">Ventas por periodo</h2><GraficoVentas serie={reporte.serie} tipo={reporte.tipo} /></div></>)}
    </div>
  );
}
