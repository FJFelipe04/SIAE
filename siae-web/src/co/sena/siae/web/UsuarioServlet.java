package co.sena.siae.web;

import co.sena.siae.dao.UsuarioDAO;
import co.sena.siae.modelo.Usuario;
import co.sena.siae.util.SeguridadClave;
import co.sena.siae.util.ValidadorUsuario;
import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.sql.SQLException;
import java.util.List;
import java.util.Optional;

/**
 * Servlet de gestión de usuarios.
 * GET  /usuarios                 -> lista y formulario vacío
 * GET  /usuarios?accion=editar&id=N -> lista y formulario con los datos del usuario
 * POST /usuarios accion=crear|actualizar|eliminar
 */
@WebServlet(name = "UsuarioServlet", urlPatterns = {"/usuarios"})
public class UsuarioServlet extends HttpServlet {

    private static final int EMPRESA_ID = 1;
    private final UsuarioDAO usuarioDao = new UsuarioDAO();

    @Override
    protected void doGet(HttpServletRequest solicitud, HttpServletResponse respuesta) throws ServletException, IOException {
        try {
            if ("editar".equals(solicitud.getParameter("accion"))) {
                usuarioDao.buscarPorId(leerEntero(solicitud.getParameter("id"))).ifPresent(u -> solicitud.setAttribute("usuarioEditar", u));
            }
            mostrar(solicitud, respuesta);
        } catch (SQLException e) {
            throw new ServletException("Error consultando usuarios", e);
        }
    }

    @Override
    protected void doPost(HttpServletRequest solicitud, HttpServletResponse respuesta) throws ServletException, IOException {
        solicitud.setCharacterEncoding("UTF-8");
        String accion = solicitud.getParameter("accion");
        try {
            switch (accion == null ? "" : accion) {
                case "crear" -> crear(solicitud);
                case "actualizar" -> actualizar(solicitud);
                case "eliminar" -> {
                    boolean eliminado = usuarioDao.eliminar(leerEntero(solicitud.getParameter("id")));
                    solicitud.setAttribute(eliminado ? "mensaje" : "errores", eliminado ? "Usuario eliminado." : List.of("El usuario no existe."));
                }
                default -> solicitud.setAttribute("errores", List.of("Acción no válida."));
            }
            mostrar(solicitud, respuesta);
        } catch (SQLException e) {
            throw new ServletException("Error guardando el usuario", e);
        }
    }

    private void crear(HttpServletRequest solicitud) throws SQLException {
        String nombre = solicitud.getParameter("nombre");
        String correo = solicitud.getParameter("correo");
        String clave = solicitud.getParameter("clave");
        String perfil = solicitud.getParameter("perfil");
        List<String> errores = ValidadorUsuario.validar(nombre, correo, clave == null ? "" : clave, perfil);
        if (errores.isEmpty() && usuarioDao.buscarPorCorreo(correo).isPresent()) {
            errores = List.of("Ya existe un usuario con ese correo.");
        }
        if (!errores.isEmpty()) {
            solicitud.setAttribute("errores", errores);
            return;
        }
        int id = usuarioDao.insertar(new Usuario(EMPRESA_ID, nombre.trim(), correo, SeguridadClave.generarHash(clave), perfil));
        solicitud.setAttribute("mensaje", "Usuario registrado con id " + id + ".");
    }

    private void actualizar(HttpServletRequest solicitud) throws SQLException {
        Optional<Usuario> encontrado = usuarioDao.buscarPorId(leerEntero(solicitud.getParameter("id")));
        if (encontrado.isEmpty()) {
            solicitud.setAttribute("errores", List.of("El usuario no existe."));
            return;
        }
        Usuario usuario = encontrado.get();
        List<String> errores = ValidadorUsuario.validar(solicitud.getParameter("nombre"), solicitud.getParameter("correo"), null, solicitud.getParameter("perfil"));
        if (!errores.isEmpty()) {
            solicitud.setAttribute("errores", errores);
            solicitud.setAttribute("usuarioEditar", usuario);
            return;
        }
        usuario.setNombre(solicitud.getParameter("nombre").trim());
        usuario.setCorreo(solicitud.getParameter("correo"));
        usuario.setPerfil(solicitud.getParameter("perfil"));
        usuario.setActivo(solicitud.getParameter("activo") != null);
        usuarioDao.actualizar(usuario);
        solicitud.setAttribute("mensaje", "Usuario " + usuario.getId() + " actualizado.");
    }

    private void mostrar(HttpServletRequest solicitud, HttpServletResponse respuesta) throws SQLException, ServletException, IOException {
        solicitud.setAttribute("usuarios", usuarioDao.listar());
        solicitud.getRequestDispatcher("/WEB-INF/jsp/usuarios.jsp").forward(solicitud, respuesta);
    }

    private int leerEntero(String texto) {
        try {
            return Integer.parseInt(texto);
        } catch (NumberFormatException e) {
            return -1;
        }
    }
}
