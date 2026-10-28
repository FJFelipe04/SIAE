import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import Alerta from "../componentes/Alerta.jsx";
import { useSesion } from "../servicios/sesion.jsx";

export default function Login() {
  const { token, iniciarSesion } = useSesion();
  const navegar = useNavigate();
  const [correo, setCorreo] = useState("");
  const [clave, setClave] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);
  if (token) return <Navigate to="/cargar" replace />;

  async function enviar(evento) {
    evento.preventDefault();
    setError("");
    setCargando(true);
    try {
      await iniciarSesion(correo, clave);
      navegar("/cargar");
    } catch (e) {
      setError(e.message);
    } finally {
      setCargando(false);
    }
  }

  return (
    <main className="container d-flex align-items-center justify-content-center" style={{ minHeight: "100vh" }}>
      <div className="card p-4" style={{ maxWidth: 420, width: "100%" }}>
        <h1 className="h3 fw-bold text-center" style={{ color: "var(--siae-azul)" }}>📊 SIAE</h1>
        <p className="text-center text-muted">Sistema de Inteligencia Analítica Empresarial</p>
        <form onSubmit={enviar}>
          <label htmlFor="correo" className="form-label">Correo electrónico</label>
          <input id="correo" type="email" className="form-control mb-3" value={correo} onChange={(e) => setCorreo(e.target.value)} autoComplete="email" required />
          <label htmlFor="clave" className="form-label">Contraseña</label>
          <input id="clave" type="password" className="form-control mb-3" value={clave} onChange={(e) => setClave(e.target.value)} autoComplete="current-password" required />
          <Alerta>{error}</Alerta>
          <button className="btn btn-siae w-100" type="submit" disabled={cargando}>{cargando ? "Ingresando…" : "Ingresar"}</button>
        </form>
        <p className="text-center mt-3 mb-0">¿No tienes cuenta? <Link to="/registro">Regístrate</Link></p>
      </div>
    </main>
  );
}
