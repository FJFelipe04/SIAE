<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ page import="java.util.List, co.sena.siae.modelo.Usuario" %>
<%!
    /** Escapa texto para mostrarlo en HTML sin riesgo de inyección. */
    private String e(Object valor) {
        if (valor == null) return "";
        return String.valueOf(valor).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;");
    }
%>
<%
    List<Usuario> usuarios = (List<Usuario>) request.getAttribute("usuarios");
    Usuario editar = (Usuario) request.getAttribute("usuarioEditar");
    List<String> errores = (List<String>) request.getAttribute("errores");
    String mensaje = (String) request.getAttribute("mensaje");
    boolean modoEditar = editar != null;
%>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SIAE – Usuarios</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>.navbar-siae{background:#1f5f99}.btn-siae{background:#1f5f99;color:#fff}</style>
</head>
<body class="bg-light">
<nav class="navbar navbar-dark navbar-siae"><div class="container-fluid"><span class="navbar-brand fw-bold">📊 SIAE · Gestión de usuarios</span></div></nav>
<main class="container py-4">
    <% if (mensaje != null) { %><div class="alert alert-success" role="status">✔ <%= e(mensaje) %></div><% } %>
    <% if (errores != null) { %><div class="alert alert-danger" role="alert"><ul class="mb-0"><% for (String error : errores) { %><li><%= e(error) %></li><% } %></ul></div><% } %>
    <div class="row g-4">
        <section class="col-lg-4">
            <div class="card p-3">
                <h1 class="h5"><%= modoEditar ? "Editar usuario " + editar.getId() : "Registrar usuario" %></h1>
                <form method="post" action="usuarios">
                    <input type="hidden" name="accion" value="<%= modoEditar ? "actualizar" : "crear" %>">
                    <% if (modoEditar) { %><input type="hidden" name="id" value="<%= editar.getId() %>"><% } %>
                    <label class="form-label" for="nombre">Nombre</label>
                    <input class="form-control mb-2" id="nombre" name="nombre" required minlength="3" value="<%= modoEditar ? e(editar.getNombre()) : "" %>">
                    <label class="form-label" for="correo">Correo</label>
                    <input class="form-control mb-2" id="correo" name="correo" type="email" required value="<%= modoEditar ? e(editar.getCorreo()) : "" %>">
                    <% if (!modoEditar) { %>
                    <label class="form-label" for="clave">Contraseña</label>
                    <input class="form-control mb-2" id="clave" name="clave" type="password" minlength="8" required>
                    <% } %>
                    <label class="form-label" for="perfil">Perfil</label>
                    <select class="form-select mb-2" id="perfil" name="perfil">
                        <option value="analista" <%= modoEditar && "analista".equals(editar.getPerfil()) ? "selected" : "" %>>Analista</option>
                        <option value="jefe_comercial" <%= modoEditar && "jefe_comercial".equals(editar.getPerfil()) ? "selected" : "" %>>Jefe comercial</option>
                    </select>
                    <% if (modoEditar) { %>
                    <div class="form-check mb-2"><input class="form-check-input" type="checkbox" id="activo" name="activo" <%= editar.isActivo() ? "checked" : "" %>><label class="form-check-label" for="activo">Activo</label></div>
                    <% } %>
                    <button class="btn btn-siae" type="submit"><%= modoEditar ? "Guardar cambios" : "Registrar" %></button>
                    <% if (modoEditar) { %><a class="btn btn-outline-secondary" href="usuarios">Cancelar</a><% } %>
                </form>
            </div>
        </section>
        <section class="col-lg-8">
            <div class="card p-3">
                <h2 class="h5">Usuarios registrados (<%= usuarios.size() %>)</h2>
                <table class="table table-sm align-middle">
                    <thead><tr><th>ID</th><th>Nombre</th><th>Correo</th><th>Perfil</th><th>Estado</th><th></th></tr></thead>
                    <tbody>
                    <% for (Usuario u : usuarios) { %>
                        <tr>
                            <td><%= u.getId() %></td><td><%= e(u.getNombre()) %></td><td><%= e(u.getCorreo()) %></td>
                            <td><%= e(u.getPerfil()) %></td><td><%= u.isActivo() ? "Activo" : "Inactivo" %></td>
                            <td class="text-nowrap">
                                <a class="btn btn-sm btn-outline-primary" href="usuarios?accion=editar&id=<%= u.getId() %>">Editar</a>
                                <form method="post" action="usuarios" class="d-inline" onsubmit="return confirm('¿Eliminar este usuario?')">
                                    <input type="hidden" name="accion" value="eliminar"><input type="hidden" name="id" value="<%= u.getId() %>">
                                    <button class="btn btn-sm btn-outline-danger" type="submit">Eliminar</button>
                                </form>
                            </td>
                        </tr>
                    <% } %>
                    </tbody>
                </table>
            </div>
        </section>
    </div>
</main>
</body>
</html>
