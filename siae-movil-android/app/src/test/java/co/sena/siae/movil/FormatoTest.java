package co.sena.siae.movil;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertNotNull;

import org.junit.Test;

public class FormatoTest {

    @Test
    public void formateaPesosColombianos() {
        assertEquals("$ 788.500", Formato.pesos(788500.0));
        assertEquals("$ 262.833", Formato.pesos(262833.33));
    }

    @Test
    public void formateaCrecimiento() {
        assertEquals("▼ 40,8 %", Formato.crecimiento(-40.81));
        assertEquals("▲ 6,3 %", Formato.crecimiento(6.3));
        assertEquals("—", Formato.crecimiento(null));
    }

    @Test
    public void barraProporcional() {
        assertEquals(10, Formato.barra(100, 100, 10).length());
        assertEquals(5, Formato.barra(50, 100, 10).length());
        assertEquals("", Formato.barra(10, 0, 10));
    }

    @Test
    public void validaLogin() {
        assertNull(ValidadorLogin.validar("laura@comercialandina.co", "Ventas2026"));
        assertNotNull(ValidadorLogin.validar("correo-malo", "x"));
        assertNotNull(ValidadorLogin.validar("laura@comercialandina.co", ""));
    }
}
