package co.sena.siae.modelo;

/**
 * Entidad Usuario de SIAE (tabla usuario).
 */
public class Usuario {

    private int id;
    private int empresaId;
    private String nombre;
    private String correo;
    private String contrasenaHash;
    private String perfil;
    private boolean activo;

    public Usuario() {
    }

    public Usuario(int empresaId, String nombre, String correo, String contrasenaHash, String perfil) {
        this.empresaId = empresaId;
        this.nombre = nombre;
        this.correo = correo;
        this.contrasenaHash = contrasenaHash;
        this.perfil = perfil;
        this.activo = true;
    }

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }
    public int getEmpresaId() { return empresaId; }
    public void setEmpresaId(int empresaId) { this.empresaId = empresaId; }
    public String getNombre() { return nombre; }
    public void setNombre(String nombre) { this.nombre = nombre; }
    public String getCorreo() { return correo; }
    public void setCorreo(String correo) { this.correo = correo; }
    public String getContrasenaHash() { return contrasenaHash; }
    public void setContrasenaHash(String contrasenaHash) { this.contrasenaHash = contrasenaHash; }
    public String getPerfil() { return perfil; }
    public void setPerfil(String perfil) { this.perfil = perfil; }
    public boolean isActivo() { return activo; }
    public void setActivo(boolean activo) { this.activo = activo; }

    @Override
    public String toString() {
        return String.format("%-4d %-22s %-32s %-15s %s", id, nombre, correo, perfil, activo ? "activo" : "inactivo");
    }
}
