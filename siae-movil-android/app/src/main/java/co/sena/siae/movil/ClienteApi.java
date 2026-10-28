package co.sena.siae.movil;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/**
 * Cliente HTTP de la API de SIAE (patrón Facade para las actividades).
 * Se debe llamar desde un hilo secundario: Android no permite red en el hilo principal.
 */
public class ClienteApi {

    private final String urlBase;
    private final String token;

    public ClienteApi(String urlBase, String token) {
        this.urlBase = urlBase;
        this.token = token;
    }

    public String iniciarSesion(String correo, String clave) throws IOException, JSONException {
        JSONObject cuerpo = new JSONObject().put("correo", correo).put("clave", clave);
        return new JSONObject(enviar("POST", "/auth/login", cuerpo.toString())).getString("access_token");
    }

    public JSONArray listarTablas() throws IOException, JSONException {
        return new JSONArray(enviar("GET", "/tablas", null));
    }

    public JSONObject generarReporte(int tablaId) throws IOException, JSONException {
        JSONObject cuerpo = new JSONObject().put("tabla_id", tablaId).put("tipo", "barras").put("agrupacion", "mes");
        return new JSONObject(enviar("POST", "/reportes", cuerpo.toString()));
    }

    private String enviar(String metodo, String ruta, String cuerpoJson) throws IOException, JSONException {
        HttpURLConnection conexion = (HttpURLConnection) new URL(urlBase + ruta).openConnection();
        conexion.setRequestMethod(metodo);
        conexion.setConnectTimeout(10_000);
        conexion.setReadTimeout(20_000);
        if (token != null) {
            conexion.setRequestProperty("Authorization", "Bearer " + token);
        }
        if (cuerpoJson != null) {
            conexion.setDoOutput(true);
            conexion.setRequestProperty("Content-Type", "application/json; charset=utf-8");
            try (OutputStream salida = conexion.getOutputStream()) {
                salida.write(cuerpoJson.getBytes(StandardCharsets.UTF_8));
            }
        }
        int codigo = conexion.getResponseCode();
        String respuesta = leer(codigo < 400 ? conexion.getInputStream() : conexion.getErrorStream());
        conexion.disconnect();
        if (codigo >= 400) {
            // La API devuelve {"detail": "mensaje"}; se muestra tal cual al usuario.
            String detalle = new JSONObject(respuesta).optString("detail", "Error " + codigo);
            throw new IOException(detalle);
        }
        return respuesta;
    }

    private static String leer(InputStream flujo) throws IOException {
        if (flujo == null) {
            return "{}";
        }
        StringBuilder texto = new StringBuilder();
        try (BufferedReader lector = new BufferedReader(new InputStreamReader(flujo, StandardCharsets.UTF_8))) {
            String linea;
            while ((linea = lector.readLine()) != null) {
                texto.append(linea);
            }
        }
        return texto.toString();
    }
}
