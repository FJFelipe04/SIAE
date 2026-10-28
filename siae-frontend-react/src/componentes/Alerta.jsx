/** Mensaje de éxito, advertencia o error, anunciado a lectores de pantalla. */
export default function Alerta({ tipo = "danger", children }) {
  if (!children) return null;
  const rol = tipo === "danger" ? "alert" : "status";
  const icono = { danger: "⚠ ", success: "✔ ", warning: "", info: "" }[tipo];
  return <div className={`alert alert-${tipo} py-2`} role={rol}>{icono}{children}</div>;
}
