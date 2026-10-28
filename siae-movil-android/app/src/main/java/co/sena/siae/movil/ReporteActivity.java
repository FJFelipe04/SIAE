package co.sena.siae.movil;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.widget.TextView;
import android.widget.Toast;
import java.util.concurrent.Executors;
import org.json.JSONArray;
import org.json.JSONObject;

/**
 * Muestra los indicadores y la serie mensual de una tabla (HU-05 y HU-06).
 */
public class ReporteActivity extends Activity {

    private final Handler principal = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle estadoGuardado) {
        super.onCreate(estadoGuardado);
        setContentView(R.layout.activity_reporte);
        int tablaId = getIntent().getIntExtra("tabla_id", -1);
        ((TextView) findViewById(R.id.tvTitulo)).setText(getIntent().getStringExtra("nombre"));
        Executors.newSingleThreadExecutor().execute(() -> {
            try {
                JSONObject reporte = new ClienteApi(BuildConfig.URL_API, Sesion.token(this)).generarReporte(tablaId);
                principal.post(() -> mostrar(reporte));
            } catch (Exception e) {
                principal.post(() -> Toast.makeText(this, e.getMessage(), Toast.LENGTH_LONG).show());
            }
        });
    }

    private void mostrar(JSONObject reporte) {
        JSONObject indicadores = reporte.optJSONObject("indicadores");
        ((TextView) findViewById(R.id.tvTotal)).setText(Formato.pesos(indicadores.optDouble("ventas_totales")));
        ((TextView) findViewById(R.id.tvPromedio)).setText(Formato.pesos(indicadores.optDouble("promedio_por_periodo")));
        Double crecimiento = indicadores.isNull("crecimiento_ultimo_periodo") ? null : indicadores.optDouble("crecimiento_ultimo_periodo");
        TextView tvCrecimiento = findViewById(R.id.tvCrecimiento);
        tvCrecimiento.setText(Formato.crecimiento(crecimiento));
        tvCrecimiento.setTextColor(crecimiento != null && crecimiento < 0 ? Color.parseColor("#B00020") : Color.parseColor("#7CB342"));
        JSONArray serie = reporte.optJSONArray("serie");
        double maximo = 0;
        for (int i = 0; i < serie.length(); i++) {
            maximo = Math.max(maximo, serie.optJSONObject(i).optDouble("total"));
        }
        StringBuilder texto = new StringBuilder();
        for (int i = 0; i < serie.length(); i++) {
            JSONObject punto = serie.optJSONObject(i);
            texto.append(punto.optString("periodo")).append("  ").append(Formato.barra(punto.optDouble("total"), maximo, 14))
                 .append("  ").append(Formato.pesos(punto.optDouble("total"))).append('\n');
        }
        ((TextView) findViewById(R.id.tvSerie)).setText(texto.toString());
    }
}
