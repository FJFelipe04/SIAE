package co.sena.siae.dao;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/**
 * Crea conexiones JDBC a PostgreSQL. Los datos se leen de variables de entorno.
 */
public final class ConexionBD {

    private static final String URL = System.getenv().getOrDefault("SIAE_JDBC_URL", "jdbc:postgresql://127.0.0.1:5432/siae");
    private static final String USUARIO = System.getenv().getOrDefault("SIAE_JDBC_USUARIO", "postgres");
    private static final String CLAVE = System.getenv().getOrDefault("SIAE_JDBC_CLAVE", "");

    static {
        try {
            // En aplicaciones web el registro automático del driver no siempre funciona: se carga explícitamente.
            Class.forName("org.postgresql.Driver");
        } catch (ClassNotFoundException e) {
            throw new ExceptionInInitializerError("No se encontró el driver JDBC de PostgreSQL en el classpath");
        }
    }

    private ConexionBD() {
    }

    public static Connection obtenerConexion() throws SQLException {
        return DriverManager.getConnection(URL, USUARIO, CLAVE);
    }
}
