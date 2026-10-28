"""Transformaciones de datos (patrón Command) y fábrica para crearlas.

Cada transformación recibe un DataFrame y devuelve uno nuevo: el original nunca se modifica.
Deshacer = volver a aplicar todos los pasos menos el último sobre el archivo original.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod

import pandas as pd


class ErrorTransformacion(ValueError):
    """Error de negocio al aplicar una transformación (columna inexistente, nombre repetido...)."""


def normalizar_fecha(valor) -> str | None:
    """Convierte dd/mm/aaaa, dd-mm-aaaa o aaaa-mm-dd a aaaa-mm-dd. Devuelve None si no es fecha.

    También acepta la hora que trae una celda de fecha de Excel ("2026-01-04 00:00:00"), que se descarta (D-10).
    """
    texto = str(valor).strip()
    m = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", texto)
    if m:
        dia, mes, anio = m.groups()
    else:
        m = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})(?:[ T]\d{1,2}:\d{2}(?::\d{2}(?:\.\d+)?)?)?", texto)
        if not m:
            return None
        anio, mes, dia = m.groups()
    try:
        return pd.Timestamp(int(anio), int(mes), int(dia)).strftime("%Y-%m-%d")
    except ValueError:  # por ejemplo 31/02/2026
        return None


def a_numero(valor) -> float | None:
    """Convierte '$ 1.250.000,50' o '120000' a número. Devuelve None si no se puede."""
    texto = re.sub(r"[$\s]", "", str(valor))
    texto = re.sub(r"\.(?=\d{3}(\D|$))", "", texto).replace(",", ".")
    try:
        return float(texto) if texto else None
    except ValueError:
        return None


class Transformacion(ABC):
    """Comando base: todas las transformaciones tienen una columna objetivo y se pueden aplicar."""

    tipo: str = ""

    def __init__(self, columna: str | None = None, **parametros):
        self.columna = columna
        self.parametros = parametros
        self.aviso: str | None = None

    def _validar_columna(self, df: pd.DataFrame) -> None:
        if self.columna not in df.columns:
            raise ErrorTransformacion(f"No existe la columna '{self.columna}'.")

    @abstractmethod
    def aplicar(self, df: pd.DataFrame) -> pd.DataFrame: ...


class EliminarColumna(Transformacion):
    tipo = "eliminar_columna"

    def aplicar(self, df):
        self._validar_columna(df)
        return df.drop(columns=[self.columna])


class RenombrarColumna(Transformacion):
    tipo = "renombrar_columna"

    def aplicar(self, df):
        self._validar_columna(df)
        nuevo = (self.parametros.get("nuevo") or "").strip()
        if not nuevo or nuevo in df.columns:
            raise ErrorTransformacion("El nuevo nombre está vacío o ya existe.")
        return df.rename(columns={self.columna: nuevo})


class FormatoFecha(Transformacion):
    tipo = "formato_fecha"

    def aplicar(self, df):
        self._validar_columna(df)
        resultado = df.copy()
        convertidas = resultado[self.columna].map(normalizar_fecha)
        errores = int(convertidas.isna().sum())
        resultado[self.columna] = convertidas.fillna(resultado[self.columna])
        self.aviso = f"{errores} fila(s) no tenían una fecha válida y se dejaron igual." if errores else None
        return resultado


class CambiarTipo(Transformacion):
    tipo = "cambiar_tipo"

    def aplicar(self, df):
        self._validar_columna(df)
        resultado = df.copy()
        if self.parametros.get("tipo", "numero") == "numero":
            numeros = resultado[self.columna].map(a_numero)
            errores = int(numeros.isna().sum())
            resultado[self.columna] = numeros.where(numeros.notna(), resultado[self.columna])
            self.aviso = f"{errores} valor(es) no se pudieron convertir a número." if errores else None
        else:
            resultado[self.columna] = resultado[self.columna].astype(str)
        return resultado


class QuitarDuplicados(Transformacion):
    tipo = "quitar_duplicados"

    def aplicar(self, df):
        return df.drop_duplicates().reset_index(drop=True)


class QuitarCaracteres(Transformacion):
    tipo = "quitar_caracteres"

    def aplicar(self, df):
        self._validar_columna(df)
        caracteres = self.parametros.get("caracteres", "")
        if not caracteres:
            raise ErrorTransformacion("Indique los caracteres a quitar.")
        patron = "[" + re.escape(caracteres) + "]"
        resultado = df.copy()
        resultado[self.columna] = resultado[self.columna].astype(str).str.replace(patron, "", regex=True)
        return resultado


class FabricaTransformaciones:
    """Factory Method: crea la transformación correcta a partir de su tipo."""

    _registro = {
        c.tipo: c
        for c in (EliminarColumna, RenombrarColumna, FormatoFecha, CambiarTipo, QuitarDuplicados, QuitarCaracteres)
    }

    @classmethod
    def crear(cls, tipo: str, columna: str | None, parametros: dict | None = None) -> Transformacion:
        if tipo not in cls._registro:
            raise ErrorTransformacion(f"Tipo de transformación no válido: {tipo}.")
        return cls._registro[tipo](columna, **(parametros or {}))


def aplicar_pasos(df: pd.DataFrame, pasos: list[tuple[str, str | None, dict]]) -> tuple[pd.DataFrame, str | None]:
    """Aplica en orden una lista de pasos (tipo, columna, parámetros). Devuelve el resultado y el último aviso."""
    aviso = None
    for tipo, columna, parametros in pasos:
        comando = FabricaTransformaciones.crear(tipo, columna, parametros)
        df = comando.aplicar(df)
        aviso = comando.aviso
    return df, aviso
