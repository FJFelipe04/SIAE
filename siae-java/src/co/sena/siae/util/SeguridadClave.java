package co.sena.siae.util;

import java.security.SecureRandom;
import java.security.spec.KeySpec;
import java.util.Base64;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;

/**
 * Protege las contraseñas con PBKDF2 (incluido en el JDK). Nunca se guardan en texto plano.
 */
public final class SeguridadClave {

    private static final int ITERACIONES = 120_000;
    private static final int LONGITUD_BITS = 256;

    private SeguridadClave() {
    }

    public static String generarHash(String clave) {
        byte[] sal = new byte[16];
        new SecureRandom().nextBytes(sal);
        return "pbkdf2$" + ITERACIONES + "$" + Base64.getEncoder().encodeToString(sal) + "$" + derivar(clave, sal, ITERACIONES);
    }

    public static boolean verificar(String clave, String hashGuardado) {
        String[] partes = hashGuardado.split("\\$");
        if (partes.length != 4 || !"pbkdf2".equals(partes[0])) {
            return false;
        }
        byte[] sal = Base64.getDecoder().decode(partes[2]);
        return derivar(clave, sal, Integer.parseInt(partes[1])).equals(partes[3]);
    }

    private static String derivar(String clave, byte[] sal, int iteraciones) {
        try {
            KeySpec especificacion = new PBEKeySpec(clave.toCharArray(), sal, iteraciones, LONGITUD_BITS);
            byte[] hash = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(especificacion).getEncoded();
            return Base64.getEncoder().encodeToString(hash);
        } catch (Exception e) {
            throw new IllegalStateException("No se pudo proteger la contraseña", e);
        }
    }
}
