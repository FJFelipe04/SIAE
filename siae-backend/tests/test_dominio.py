"""Pruebas unitarias del dominio (no usan base de datos)."""
import pandas as pd
import pytest

from app.dominio.transformaciones import ErrorTransformacion, FabricaTransformaciones, a_numero, aplicar_pasos, normalizar_fecha


@pytest.mark.parametrize("entrada,esperado", [("01/08/2026", "2026-08-01"), ("2-9-2026", "2026-09-02"), ("2026-09-10", "2026-09-10"),
                                              ("31/02/2026", None), ("sin fecha", None), ("", None)])
def test_normalizar_fecha(entrada, esperado):
    assert normalizar_fecha(entrada) == esperado


@pytest.mark.parametrize("entrada,esperado", [("120.000", 120000), ("$ 210.500", 210500), ("1.250.000,50", 1250000.5), ("15", 15), ("abc", None), ("", None)])
def test_a_numero(entrada, esperado):
    assert a_numero(entrada) == esperado


def test_original_no_cambia_y_deshacer_por_reaplicacion():
    df = pd.DataFrame({"Fecha": ["01/08/2026", "01/08/2026"], "Valor": ["1.000", "1.000"], "Obs": ["x", "x"]})
    pasos = [("quitar_duplicados", None, {}), ("eliminar_columna", "Obs", {})]
    resultado, _ = aplicar_pasos(df, pasos)
    assert list(resultado.columns) == ["Fecha", "Valor"] and len(resultado) == 1
    deshecho, _ = aplicar_pasos(df, pasos[:-1])
    assert "Obs" in deshecho.columns
    assert len(df) == 2 and "Obs" in df.columns


def test_errores_de_negocio():
    df = pd.DataFrame({"A": ["1"], "B": ["2"]})
    with pytest.raises(ErrorTransformacion):
        FabricaTransformaciones.crear("eliminar_columna", "Z").aplicar(df)
    with pytest.raises(ErrorTransformacion):
        FabricaTransformaciones.crear("renombrar_columna", "A", {"nuevo": "B"}).aplicar(df)
    with pytest.raises(ErrorTransformacion):
        FabricaTransformaciones.crear("tipo_inventado", "A")
