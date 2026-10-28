import { createContext, useContext, useState } from "react";
import { llamarApi } from "./api.js";

/** Contexto con el token y el usuario autenticado, disponible en toda la aplicación. */
const ContextoSesion = createContext(null);

export function SesionProvider({ children }) {
  const [token, setToken] = useState(() => sessionStorage.getItem("siae_token"));
  const [correo, setCorreo] = useState(() => sessionStorage.getItem("siae_correo"));

  async function iniciarSesion(correoIngresado, clave) {
    const datos = await llamarApi("/auth/login", { metodo: "POST", cuerpo: { correo: correoIngresado, clave } });
    sessionStorage.setItem("siae_token", datos.access_token);
    sessionStorage.setItem("siae_correo", correoIngresado);
    setToken(datos.access_token);
    setCorreo(correoIngresado);
  }

  function cerrarSesion() {
    sessionStorage.clear();
    setToken(null);
    setCorreo(null);
  }

  /** Llama a la API con el token; si la sesión expiró, la cierra. */
  async function api(ruta, opciones = {}) {
    try {
      return await llamarApi(ruta, { ...opciones, token });
    } catch (error) {
      if (error.estado === 401) cerrarSesion();
      throw error;
    }
  }

  return <ContextoSesion.Provider value={{ token, correo, iniciarSesion, cerrarSesion, api }}>{children}</ContextoSesion.Provider>;
}

export const useSesion = () => useContext(ContextoSesion);
