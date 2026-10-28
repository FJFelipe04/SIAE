package co.sena.siae;

import co.sena.siae.dao.UsuarioDAO;
import co.sena.siae.modelo.Usuario;
import co.sena.siae.util.SeguridadClave;
import co.sena.siae.util.ValidadorUsuario;
import java.sql.SQLException;
import java.util.List;
import java.util.Optional;
import java.util.Scanner;

/**
 * Módulo de gestión de usuarios de SIAE por consola (CRUD con JDBC).
 * Uso: java co.sena.siae.AplicacionUsuarios          (menú interactivo)
 *      java co.sena.siae.AplicacionUsuarios --demo   (ejecuta el CRUD completo de ejemplo)
 */
public class AplicacionUsuarios {

    private static final int EMPRESA_ID = 1;
    private final UsuarioDAO usuarioDao = new UsuarioDAO();
    private final Scanner lector = new Scanner(System.in);

    public static void main(String[] args) {
        AplicacionUsuarios aplicacion = new AplicacionUsuarios();
        try {
            if (args.length > 0 && "--demo".equals(args[0])) {
                aplicacion.ejecutarDemostracion();
            } else {
                aplicacion.mostrarMenu();
            }
        } catch (SQLException e) {
            System.out.println("Error de base de datos: " + e.getMessage());
        }
    }

    private void mostrarMenu() throws SQLException {
        String opcion;
        do {
            System.out.println("\n=== SIAE - Gestión de usuarios ===");
            System.out.println("1. Registrar  2. Listar  3. Buscar  4. Actualizar  5. Eliminar  0. Salir");
            System.out.print("Opción: ");
            opcion = lector.nextLine().trim();
            switch (opcion) {
                case "1" -> registrar(pedir("Nombre"), pedir("Correo"), pedir("Contraseña"), pedir("Perfil (analista/jefe_comercial)"));
                case "2" -> imprimir(usuarioDao.listar());
                case "3" -> System.out.println(usuarioDao.buscarPorId(pedirEntero("Id")).map(Usuario::toString).orElse("No existe."));
                case "4" -> actualizar(pedirEntero("Id"), pedir("Nuevo nombre"), pedir("Nuevo perfil"));
                case "5" -> System.out.println(usuarioDao.eliminar(pedirEntero("Id")) ? "Usuario eliminado." : "No existe.");
                case "0" -> System.out.println("Hasta luego.");
                default -> System.out.println("Opción no válida.");
            }
        } while (!"0".equals(opcion));
    }

    /** Valida los datos, verifica que el correo no exista y registra el usuario. */
    int registrar(String nombre, String correo, String clave, String perfil) throws SQLException {
        List<String> errores = ValidadorUsuario.validar(nombre, correo, clave, perfil);
        if (!errores.isEmpty()) {
            errores.forEach(error -> System.out.println("  ✗ " + error));
            return -1;
        }
        if (usuarioDao.buscarPorCorreo(correo).isPresent()) {
            System.out.println("  ✗ Ya existe un usuario con ese correo.");
            return -1;
        }
        int id = usuarioDao.insertar(new Usuario(EMPRESA_ID, nombre.trim(), correo, SeguridadClave.generarHash(clave), perfil));
        System.out.println("  ✓ Usuario registrado con id " + id);
        return id;
    }

    void actualizar(int id, String nombre, String perfil) throws SQLException {
        Optional<Usuario> encontrado = usuarioDao.buscarPorId(id);
        if (encontrado.isEmpty()) {
            System.out.println("  ✗ No existe el usuario " + id);
            return;
        }
        Usuario usuario = encontrado.get();
        List<String> errores = ValidadorUsuario.validar(nombre, usuario.getCorreo(), null, perfil);
        if (!errores.isEmpty()) {
            errores.forEach(error -> System.out.println("  ✗ " + error));
            return;
        }
        usuario.setNombre(nombre);
        usuario.setPerfil(perfil);
        usuarioDao.actualizar(usuario);
        System.out.println("  ✓ Usuario " + id + " actualizado");
    }

    private void ejecutarDemostracion() throws SQLException {
        System.out.println("1) INSERTAR");
        int id = registrar("Laura Gómez", "laura.java@comercialandina.co", "Ventas2026", "analista");
        registrar("Carlos Ruiz", "carlos.java@comercialandina.co", "Reportes2026", "jefe_comercial");
        System.out.println("   Validaciones:");
        registrar("A", "correo-malo", "123", "gerente");
        registrar("Laura Repetida", "laura.java@comercialandina.co", "Ventas2026", "analista");
        System.out.println("2) CONSULTAR (listar)");
        imprimir(usuarioDao.listar());
        System.out.println("3) ACTUALIZAR id " + id);
        actualizar(id, "Laura Gómez Pérez", "jefe_comercial");
        System.out.println("   " + usuarioDao.buscarPorId(id).orElseThrow());
        System.out.println("   Contraseña correcta: " + SeguridadClave.verificar("Ventas2026", usuarioDao.buscarPorId(id).orElseThrow().getContrasenaHash()));
        System.out.println("4) ELIMINAR id " + id);
        System.out.println("   Eliminado: " + usuarioDao.eliminar(id));
        imprimir(usuarioDao.listar());
    }

    private void imprimir(List<Usuario> usuarios) {
        System.out.println(String.format("   %-4s %-22s %-32s %-15s %s", "ID", "NOMBRE", "CORREO", "PERFIL", "ESTADO"));
        usuarios.forEach(u -> System.out.println("   " + u));
    }

    private String pedir(String etiqueta) {
        System.out.print(etiqueta + ": ");
        return lector.nextLine();
    }

    private int pedirEntero(String etiqueta) {
        try {
            return Integer.parseInt(pedir(etiqueta).trim());
        } catch (NumberFormatException e) {
            return -1;
        }
    }
}
