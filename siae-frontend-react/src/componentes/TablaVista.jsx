/** Tabla de vista previa: muestra columnas y filas tal como llegan de la API. */
export default function TablaVista({ vista }) {
  if (!vista) return null;
  return (
    <div className="table-responsive">
      <table className="table table-sm table-striped bg-white vista">
        <thead>
          <tr>{vista.columnas.map((c) => <th key={c} scope="col">{c}</th>)}</tr>
        </thead>
        <tbody>
          {vista.filas.map((fila, i) => (
            <tr key={i}>{fila.map((valor, j) => <td key={j}>{valor === null ? "" : String(valor)}</td>)}</tr>
          ))}
        </tbody>
      </table>
      <p className="small text-muted">{vista.total_filas} filas · {vista.columnas.length} columnas{vista.total_filas > vista.filas.length ? ` (se muestran ${vista.filas.length})` : ""}</p>
    </div>
  );
}
