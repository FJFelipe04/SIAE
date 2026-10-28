package co.sena.siae.dao;

import co.sena.siae.modelo.Usuario;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * DAO de usuarios: inserción, consulta, actualización y eliminación con JDBC.
 * Todas las consultas usan PreparedStatement para evitar inyección SQL.
 */
public class UsuarioDAO {

    private static final String SQL_INSERTAR =
            "INSERT INTO usuario (empresa_id, nombre, correo, contrasena_hash, perfil) VALUES (?, ?, ?, ?, ?)";
    private static final String SQL_BUSCAR_POR_ID =
            "SELECT id, empresa_id, nombre, correo, contrasena_hash, perfil, activo FROM usuario WHERE id = ?";
    private static final String SQL_BUSCAR_POR_CORREO =
            "SELECT id, empresa_id, nombre, correo, contrasena_hash, perfil, activo FROM usuario WHERE correo = ?";
    private static final String SQL_LISTAR =
            "SELECT id, empresa_id, nombre, correo, contrasena_hash, perfil, activo FROM usuario ORDER BY id";
    private static final String SQL_ACTUALIZAR =
            "UPDATE usuario SET nombre = ?, correo = ?, perfil = ?, activo = ? WHERE id = ?";
    private static final String SQL_ELIMINAR = "DELETE FROM usuario WHERE id = ?";

    /** Inserta un usuario y devuelve el id generado. */
    public int insertar(Usuario usuario) throws SQLException {
        try (Connection conexion = ConexionBD.obtenerConexion();
             PreparedStatement sentencia = conexion.prepareStatement(SQL_INSERTAR, Statement.RETURN_GENERATED_KEYS)) {
            sentencia.setInt(1, usuario.getEmpresaId());
            sentencia.setString(2, usuario.getNombre());
            sentencia.setString(3, usuario.getCorreo().toLowerCase());
            sentencia.setString(4, usuario.getContrasenaHash());
            sentencia.setString(5, usuario.getPerfil());
            sentencia.executeUpdate();
            try (ResultSet llaves = sentencia.getGeneratedKeys()) {
                llaves.next();
                usuario.setId(llaves.getInt(1));
                return usuario.getId();
            }
        }
    }

    public Optional<Usuario> buscarPorId(int id) throws SQLException {
        return buscarUno(SQL_BUSCAR_POR_ID, id);
    }

    public Optional<Usuario> buscarPorCorreo(String correo) throws SQLException {
        return buscarUno(SQL_BUSCAR_POR_CORREO, correo.toLowerCase());
    }

    public List<Usuario> listar() throws SQLException {
        List<Usuario> usuarios = new ArrayList<>();
        try (Connection conexion = ConexionBD.obtenerConexion();
             PreparedStatement sentencia = conexion.prepareStatement(SQL_LISTAR);
             ResultSet resultado = sentencia.executeQuery()) {
            while (resultado.next()) {
                usuarios.add(mapear(resultado));
            }
        }
        return usuarios;
    }

    /** Actualiza nombre, correo, perfil y estado. Devuelve true si encontró el usuario. */
    public boolean actualizar(Usuario usuario) throws SQLException {
        try (Connection conexion = ConexionBD.obtenerConexion();
             PreparedStatement sentencia = conexion.prepareStatement(SQL_ACTUALIZAR)) {
            sentencia.setString(1, usuario.getNombre());
            sentencia.setString(2, usuario.getCorreo().toLowerCase());
            sentencia.setString(3, usuario.getPerfil());
            sentencia.setBoolean(4, usuario.isActivo());
            sentencia.setInt(5, usuario.getId());
            return sentencia.executeUpdate() == 1;
        }
    }

    public boolean eliminar(int id) throws SQLException {
        try (Connection conexion = ConexionBD.obtenerConexion();
             PreparedStatement sentencia = conexion.prepareStatement(SQL_ELIMINAR)) {
            sentencia.setInt(1, id);
            return sentencia.executeUpdate() == 1;
        }
    }

    private Optional<Usuario> buscarUno(String sql, Object parametro) throws SQLException {
        try (Connection conexion = ConexionBD.obtenerConexion();
             PreparedStatement sentencia = conexion.prepareStatement(sql)) {
            sentencia.setObject(1, parametro);
            try (ResultSet resultado = sentencia.executeQuery()) {
                return resultado.next() ? Optional.of(mapear(resultado)) : Optional.empty();
            }
        }
    }

    private Usuario mapear(ResultSet fila) throws SQLException {
        Usuario usuario = new Usuario();
        usuario.setId(fila.getInt("id"));
        usuario.setEmpresaId(fila.getInt("empresa_id"));
        usuario.setNombre(fila.getString("nombre"));
        usuario.setCorreo(fila.getString("correo"));
        usuario.setContrasenaHash(fila.getString("contrasena_hash"));
        usuario.setPerfil(fila.getString("perfil"));
        usuario.setActivo(fila.getBoolean("activo"));
        return usuario;
    }
}
