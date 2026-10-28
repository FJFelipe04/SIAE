import { NavLink, useNavigate } from "react-router-dom";
import { useSesion } from "../servicios/sesion.jsx";

export default function BarraNavegacion() {
  const { correo, esAdmin, cerrarSesion } = useSesion();
  const navegar = useNavigate();
  const enlace = ({ isActive }) => "nav-link" + (isActive ? " active fw-semibold" : "");
  return (
    <nav className="navbar navbar-expand-md navbar-dark navbar-siae">
      <div className="container-fluid">
        <span className="navbar-brand fw-bold">📊 SIAE</span>
        <ul className="navbar-nav me-auto flex-row gap-3">
          <li className="nav-item"><NavLink className={enlace} to="/cargar">Cargar archivo</NavLink></li>
          <li className="nav-item"><NavLink className={enlace} to="/tablas">Mis tablas</NavLink></li>
          <li className="nav-item"><NavLink className={enlace} to="/reportes">Reportes</NavLink></li>
          {esAdmin && <li className="nav-item"><NavLink className={enlace} to="/admin">Administración</NavLink></li>}
        </ul>
        <span className="navbar-text me-3 text-white-50">{esAdmin && <span className="badge bg-warning text-dark me-2">Administrador</span>}{correo}</span>
        <button className="btn btn-outline-light btn-sm" onClick={() => { cerrarSesion(); navegar("/login"); }}>Cerrar sesión</button>
      </div>
    </nav>
  );
}
