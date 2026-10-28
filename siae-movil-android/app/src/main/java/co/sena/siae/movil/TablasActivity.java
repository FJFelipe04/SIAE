package co.sena.siae.movil;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import org.json.JSONArray;
import org.json.JSONObject;

/**
 * Lista las tablas transformadas del usuario (HU-04). Al tocar una se abre su reporte.
 */
public class TablasActivity extends Activity {

    private final Handler principal = new Handler(Looper.getMainLooper());
    private final List<Integer> ids = new ArrayList<>();
    private final List<String> nombres = new ArrayList<>();

    @Override
    protected void onCreate(Bundle estadoGuardado) {
        super.onCreate(estadoGuardado);
        setContentView(R.layout.activity_tablas);
        ListView lista = findViewById(R.id.lvTablas);
        TextView vacio = findViewById(R.id.tvVacio);
        Button cerrar = findViewById(R.id.btnCerrar);
        cerrar.setOnClickListener(v -> {
            Sesion.cerrar(this);
            startActivity(new Intent(this, LoginActivity.class));
            finish();
        });
        lista.setOnItemClickListener((padre, vista, posicion, id) -> {
            Intent reporte = new Intent(this, ReporteActivity.class);
            reporte.putExtra("tabla_id", ids.get(posicion));
            reporte.putExtra("nombre", nombres.get(posicion));
            startActivity(reporte);
        });
        Executors.newSingleThreadExecutor().execute(() -> {
            try {
                JSONArray tablas = new ClienteApi(BuildConfig.URL_API, Sesion.token(this)).listarTablas();
                List<String> filas = new ArrayList<>();
                for (int i = 0; i < tablas.length(); i++) {
                    JSONObject tabla = tablas.getJSONObject(i);
                    ids.add(tabla.getInt("id"));
                    nombres.add(tabla.getString("nombre"));
                    filas.add(tabla.getString("nombre") + "  ·  " + tabla.getInt("filas") + " filas");
                }
                principal.post(() -> {
                    lista.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, filas));
                    vacio.setVisibility(filas.isEmpty() ? View.VISIBLE : View.GONE);
                });
            } catch (Exception e) {
                principal.post(() -> Toast.makeText(this, e.getMessage(), Toast.LENGTH_LONG).show());
            }
        });
    }
}
