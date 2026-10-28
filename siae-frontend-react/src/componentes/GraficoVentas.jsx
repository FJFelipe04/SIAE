import { ArcElement, BarElement, CategoryScale, Chart as ChartJS, Legend, LinearScale, LineElement, PointElement, Tooltip } from "chart.js";
import { Bar, Line, Pie } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Tooltip, Legend);
const COLORES = ["#1f5f99", "#7cb342", "#263238", "#90a4ae", "#5c8fc2", "#aed581"];

/** Gráfico de ventas por periodo (líneas, barras o torta). */
export default function GraficoVentas({ serie, tipo }) {
  if (!serie?.length) return <div className="alert alert-info">Sin datos para el periodo.</div>;
  const datos = { labels: serie.map((s) => s.periodo), datasets: [{ label: "Ventas", data: serie.map((s) => s.total), borderColor: "#1f5f99", backgroundColor: COLORES }] };
  const opciones = { animation: false, plugins: { legend: { display: tipo === "torta" } } };
  const Componente = { lineas: Line, barras: Bar, torta: Pie, tabla_dinamica: Bar }[tipo] || Line;
  return <div role="img" aria-label="Gráfico de ventas por periodo" style={{ maxHeight: 320 }}><Componente data={datos} options={opciones} height={90} /></div>;
}
