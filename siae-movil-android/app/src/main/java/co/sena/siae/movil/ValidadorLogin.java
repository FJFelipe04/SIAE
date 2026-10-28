package co.sena.siae.movil;

import java.util.regex.Pattern;

/**
 * Valida los datos del formulario antes de llamar a la API.
 */
public final class ValidadorLogin {

    private static final Pattern CORREO = Pattern.compile("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$");

    private ValidadorLogin() {
    }

    /** Devuelve null si los datos son válidos o el mensaje de error. */
    public static String validar(String correo, String clave) {
        if (correo == null || !CORREO.matcher(correo.trim()).matches()) {
            return "Escribe un correo válido.";
        }
        if (clave == null || clave.isEmpty()) {
            return "Escribe tu contraseña.";
        }
        return null;
    }
}
