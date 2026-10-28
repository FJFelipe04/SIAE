package co.sena.miprimeraapp;

import android.app.Activity;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;

/**
 * Actividad principal: muestra un mensaje y cuenta los toques del botón.
 */
public class MainActivity extends Activity {

    private int toques = 0;

    @Override
    protected void onCreate(Bundle estadoGuardado) {
        super.onCreate(estadoGuardado);
        setContentView(R.layout.activity_main);
        TextView mensaje = findViewById(R.id.tvMensaje);
        Button boton = findViewById(R.id.btnSaludar);
        boton.setOnClickListener(v -> {
            toques++;
            mensaje.setText("Hola, soy Juan Felipe Perdomo – ADSO SENA.\nHas tocado el botón " + toques + " vez/veces.");
        });
    }
}
