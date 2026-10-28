package co.sena.siae.movil;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.TextView;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Pantalla de inicio de sesión (HU-01).
 */
public class LoginActivity extends Activity {

    private final ExecutorService hilo = Executors.newSingleThreadExecutor();
    private final Handler principal = new Handler(Looper.getMainLooper());
    private EditText etCorreo;
    private EditText etClave;
    private TextView tvError;
    private ProgressBar progreso;
    private Button btnIngresar;

    @Override
    protected void onCreate(Bundle estadoGuardado) {
        super.onCreate(estadoGuardado);
        if (Sesion.token(this) != null) {
            abrirTablas();
            return;
        }
        setContentView(R.layout.activity_login);
        etCorreo = findViewById(R.id.etCorreo);
        etClave = findViewById(R.id.etClave);
        tvError = findViewById(R.id.tvError);
        progreso = findViewById(R.id.progreso);
        btnIngresar = findViewById(R.id.btnIngresar);
        btnIngresar.setOnClickListener(v -> ingresar());
    }

    private void ingresar() {
        String correo = etCorreo.getText().toString().trim();
        String clave = etClave.getText().toString();
        String error = ValidadorLogin.validar(correo, clave);
        if (error != null) {
            mostrarError(error);
            return;
        }
        cargando(true);
        hilo.execute(() -> {
            try {
                String token = new ClienteApi(BuildConfig.URL_API, null).iniciarSesion(correo, clave);
                principal.post(() -> {
                    Sesion.guardar(this, token);
                    abrirTablas();
                });
            } catch (Exception e) {
                principal.post(() -> {
                    cargando(false);
                    mostrarError(e.getMessage() == null ? "No se pudo conectar con el servidor." : e.getMessage());
                });
            }
        });
    }

    private void abrirTablas() {
        startActivity(new Intent(this, TablasActivity.class));
        finish();
    }

    private void mostrarError(String mensaje) {
        tvError.setText(mensaje);
        tvError.setVisibility(View.VISIBLE);
    }

    private void cargando(boolean activo) {
        progreso.setVisibility(activo ? View.VISIBLE : View.GONE);
        btnIngresar.setEnabled(!activo);
    }

    @Override
    protected void onDestroy() {
        hilo.shutdown();
        super.onDestroy();
    }
}
