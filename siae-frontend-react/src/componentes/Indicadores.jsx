const pesos = (n) => "$ " + Math.round(n).toLocaleString("es-CO");

/** Tarjetas de indicadores del reporte (HU-06). */
export default function Indicadores({ indicadores }) {
  if (!indicadores) return null;
  const c = indicadores.crecimiento_ultimo_periodo;
  return (
    <div className="row g-3 mb-3">
      <div className="col-md-4"><div className="card p-3"><div className="small text-muted">Ventas totales</div><div className="kpi" data-kpi="total">{pesos(indicadores.ventas_totales)}</div></div></div>
      <div className="col-md-4"><div className="card p-3"><div className="small text-muted">Promedio por periodo</div><div className="kpi">{pesos(indicadores.promedio_por_periodo)}</div></div></div>
      <div className="col-md-4"><div className="card p-3"><div className="small text-muted">Crecimiento último periodo</div>
        <div className="kpi" data-kpi="crecimiento" style={{ color: c < 0 ? "#b00020" : "var(--siae-verde)" }}>{c === null ? "—" : `${c >= 0 ? "▲" : "▼"} ${Math.abs(c).toFixed(1)} %`}</div></div></div>
    </div>
  );
}
