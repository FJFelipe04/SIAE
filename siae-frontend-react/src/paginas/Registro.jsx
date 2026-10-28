import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Alerta from "../componentes/Alerta.jsx";
import { llamarApi } from "../servicios/api.js";

export default function Registro() {
  const navegar = useNavigate();
  const [datos, setDatos] = useState({ nombre: "", correo: "", clave: "", perfil: "analista" });
  const [error, setError] = useState("");
  const cambiar = (campo) => (e) => setDatos({ ...datos, [campo]: e.target.value });

  async function enviar(evento) {
    evento.preventDefault();
    if (datos.clave.length < 8) return setError("La contraseña debe tener mínimo 8 caracteres.");
    try {
      await llamarApi("/auth/registro", { metodo: "POST", cuerpo: datos });
      navegar("/login");
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <main className="container py-5" style={{ maxWidth: 520 }}>
      <div className="card p-4">
        <h1 className="h4">Crear cuenta</h1>
        <form onSubmit={enviar}>
          <label htmlFor="nombre" className="form-label">Nombre completo</label>
          <input id="nombre" className="form-control mb-2" value={datos.nombre} onChange={cambiar("nombre")} minLength={3} required />
          <label htmlFor="correoR" className="form-label">Correo</label>
          <input id="correoR" type="email" className="form-control mb-2" value={datos.correo} onChange={cambiar("correo")} required />
          <label htmlFor="claveR" className="form-label">Contraseña</label>
          <input id="claveR" type="password" className="form-control mb-1" value={datos.clave} onChange={cambiar("clave")} aria-describedby="ayudaClave" required />
          <div id="ayudaClave" className="form-text mb-2">Mínimo 8 caracteres.</div>
          <label htmlFor="perfil" className="form-label">Perfil</label>
          <select id="perfil" className="form-select mb-3" value={datos.perfil} onChange={cambiar("perfil")}>
            <option value="analista">Analista</option>
            <option value="jefe_comercial">Jefe comercial</option>
          </select>
          <Alerta>{error}</Alerta>
          <button className="btn btn-siae me-2" type="submit">Registrarme</button>
          <Link className="btn btn-outline-secondary" to="/login">Cancelar</Link>
        </form>
      </div>
    </main>
  );
}
