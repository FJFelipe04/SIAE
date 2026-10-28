package co.sena.siae.util;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;

/**
 * Reglas de validación de los datos de un usuario (HU-01).
 */
public final class ValidadorUsuario {

    private static final Pattern PATRON_CORREO = Pattern.compile("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$");
    private static final int LONGITUD_MINIMA_CLAVE = 8;

    private ValidadorUsuario() {
    }

    public static List<String> validar(String nombre, String correo, String clave, String perfil) {
        List<String> errores = new ArrayList<>();
        if (nombre == null || nombre.trim().length() < 3 || nombre.length() > 100) {
            errores.add("El nombre debe tener entre 3 y 100 caracteres.");
        }
        if (correo == null || !PATRON_CORREO.matcher(correo).matches()) {
            errores.add("El correo no es válido.");
        }
        if (clave != null && clave.length() < LONGITUD_MINIMA_CLAVE) {
            errores.add("La contraseña debe tener mínimo 8 caracteres.");
        }
        if (!"analista".equals(perfil) && !"jefe_comercial".equals(perfil)) {
            errores.add("El perfil debe ser analista o jefe_comercial.");
        }
        return errores;
    }
}
