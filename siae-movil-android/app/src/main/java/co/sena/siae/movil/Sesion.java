package co.sena.siae.movil;

import android.content.Context;
import android.content.SharedPreferences;

/**
 * Guarda el token de la sesión en las preferencias privadas de la app.
 */
public final class Sesion {

    private static final String ARCHIVO = "siae_sesion";
    private static final String CLAVE_TOKEN = "token";

    private Sesion() {
    }

    public static void guardar(Context contexto, String token) {
        preferencias(contexto).edit().putString(CLAVE_TOKEN, token).apply();
    }

    public static String token(Context contexto) {
        return preferencias(contexto).getString(CLAVE_TOKEN, null);
    }

    public static void cerrar(Context contexto) {
        preferencias(contexto).edit().clear().apply();
    }

    private static SharedPreferences preferencias(Context contexto) {
        return contexto.getSharedPreferences(ARCHIVO, Context.MODE_PRIVATE);
    }
}
