import { Navigate, Route, Routes } from "react-router-dom";
import BarraNavegacion from "./componentes/BarraNavegacion.jsx";
import { useSesion } from "./servicios/sesion.jsx";
import Login from "./paginas/Login.jsx";
import Registro from "./paginas/Registro.jsx";
import CargarArchivo from "./paginas/CargarArchivo.jsx";
import Transformar from "./paginas/Transformar.jsx";
import MisTablas from "./paginas/MisTablas.jsx";
import Reportes from "./paginas/Reportes.jsx";

/** Envuelve las páginas que exigen sesión iniciada. */
function RutaPrivada({ children }) {
  const { token } = useSesion();
  return token ? (
    <>
      <BarraNavegacion />
      <main className="container-fluid py-4">{children}</main>
    </>
  ) : (
    <Navigate to="/login" replace />
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/registro" element={<Registro />} />
      <Route path="/cargar" element={<RutaPrivada><CargarArchivo /></RutaPrivada>} />
      <Route path="/transformar/:sesionId" element={<RutaPrivada><Transformar /></RutaPrivada>} />
      <Route path="/tablas" element={<RutaPrivada><MisTablas /></RutaPrivada>} />
      <Route path="/reportes" element={<RutaPrivada><Reportes /></RutaPrivada>} />
      <Route path="*" element={<Navigate to="/cargar" replace />} />
    </Routes>
  );
}
