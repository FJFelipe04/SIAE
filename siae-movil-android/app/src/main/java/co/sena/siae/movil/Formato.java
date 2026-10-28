package co.sena.siae.movil;

import java.text.NumberFormat;
import java.util.Locale;

/**
 * Formatos de presentación (lógica pura, sin dependencias de Android: se prueba con JUnit).
 */
public final class Formato {

    private static final Locale COLOMBIA = Locale.forLanguageTag("es-CO");

    private Formato() {
    }

    /** 788500.0 -> "$ 788.500" */
    public static String pesos(double valor) {
        NumberFormat formato = NumberFormat.getIntegerInstance(COLOMBIA);
        return "$ " + formato.format(Math.round(valor));
    }

    /** -40.81 -> "▼ 40,8 %"; null -> "—" */
    public static String crecimiento(Double porcentaje) {
        if (porcentaje == null) {
            return "—";
        }
        String flecha = porcentaje >= 0 ? "▲ " : "▼ ";
        return flecha + String.format(COLOMBIA, "%.1f %%", Math.abs(porcentaje));
    }

    /** Barra de texto proporcional para mostrar la serie sin librerías de gráficos. */
    public static String barra(double valor, double maximo, int ancho) {
        if (maximo <= 0) {
            return "";
        }
        int largo = (int) Math.round(valor / maximo * ancho);
        // StringBuilder en lugar de String.repeat, que no existe en Android 7 (minSdk 24)
        StringBuilder barra = new StringBuilder();
        for (int i = 0; i < largo; i++) {
            barra.append('█');
        }
        return barra.toString();
    }
}
