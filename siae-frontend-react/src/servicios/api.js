/**
 * Cliente de la API de SIAE. Agrega el token y convierte los errores en mensajes legibles.
 */
const URL_API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export class ErrorApi extends Error {
  constructor(mensaje, estado) {
    super(mensaje);
    this.estado = estado;
  }
}

function mensajeDeError(cuerpo) {
  if (!cuerpo || !cuerpo.detail) return "Ocurrió un error inesperado.";
  if (typeof cuerpo.detail === "string") return cuerpo.detail;
  // Errores de validación de FastAPI: lista de {loc, msg}
  return cuerpo.detail.map((e) => `${e.loc.at(-1)}: ${e.msg}`).join(" · ");
}

export async function llamarApi(ruta, { metodo = "GET", cuerpo, token, archivo, binario = false } = {}) {
  const encabezados = {};
  if (token) encabezados.Authorization = `Bearer ${token}`;
  let body;
  if (archivo) {
    body = new FormData();
    body.append("archivo", archivo);
  } else if (cuerpo !== undefined) {
    encabezados["Content-Type"] = "application/json";
    body = JSON.stringify(cuerpo);
  }
  const respuesta = await fetch(URL_API + ruta, { method: metodo, headers: encabezados, body });
  if (!respuesta.ok) {
    const datos = await respuesta.json().catch(() => null);
    throw new ErrorApi(mensajeDeError(datos), respuesta.status);
  }
  if (respuesta.status === 204) return null;
  return binario ? respuesta.blob() : respuesta.json();
}
