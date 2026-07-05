"""Perfilado de calidad de datos: diagnostica problemas sin modificar
los datos (duplicados, nulos, tipos, rangos, integridad referencial).
La limpieza vive en clean.py.
"""

import pandas as pd


def perfilar(df: pd.DataFrame, nombre_fuente: str, llave=None) -> dict:
  
    perfil = {
        "fuente": nombre_fuente,
        "filas": len(df),
        "duplicados_totales": int(df.duplicated().sum()),
        "nulos_por_columna": df.isna().sum().to_dict(),
        "tipos_por_columna": df.dtypes.astype(str).to_dict(),
    }

    columnas_llave = [llave] if isinstance(llave, str) else llave
    if columnas_llave and all(col in df.columns for col in columnas_llave):
        perfil["duplicados_por_llave"] = int(df.duplicated(subset=columnas_llave).sum())

    columnas_numericas = df.select_dtypes(include="number").columns
    if len(columnas_numericas) > 0:
        perfil["rangos_numericos"] = {
            col: {"min": df[col].min(), "max": df[col].max()} for col in columnas_numericas
        }

    return perfil


def formatear_perfil_markdown(perfil: dict) -> str:
    lineas = [f"## {perfil['fuente']}", ""]
    lineas.append(f"- Filas: {perfil['filas']}")
    lineas.append(f"- Duplicados (fila completa): {perfil['duplicados_totales']}")

    if "duplicados_por_llave" in perfil:
        lineas.append(f"- Duplicados por llave: {perfil['duplicados_por_llave']}")

    nulos = {c: n for c, n in perfil["nulos_por_columna"].items() if n > 0}
    if nulos:
        lineas.append("- Nulos por columna:")
        lineas.extend(f"  - `{col}`: {n}" for col, n in nulos.items())
    else:
        lineas.append("- Nulos por columna: ninguno")

    lineas.append("- Tipos de dato al leer el archivo crudo:")
    lineas.extend(f"  - `{col}`: {tipo}" for col, tipo in perfil["tipos_por_columna"].items())

    if "rangos_numericos" in perfil:
        lineas.append("- Rangos numéricos (revisar valores fuera de lo esperado):")
        for col, rango in perfil["rangos_numericos"].items():
            lineas.append(f"  - `{col}`: min={rango['min']}, max={rango['max']}")

    lineas.append("")
    return "\n".join(lineas)


def verificar_integridad_referencial(
    df_hijo: pd.DataFrame, columna_hijo: str, ids_validos, nombre_relacion: str
) -> dict:
    """Cuenta cuántos valores de `columna_hijo` no existen en `ids_validos`
    (la llave de la tabla padre). No modifica nada, solo diagnostica.
    """
    huerfanos = ~df_hijo[columna_hijo].isin(ids_validos)
    valores = sorted(df_hijo.loc[huerfanos, columna_hijo].dropna().unique().tolist())
    return {"relacion": nombre_relacion, "huerfanos": int(huerfanos.sum()), "valores_huerfanos": valores}


def formatear_integridad_markdown(resultado: dict) -> str:
    if resultado["huerfanos"] == 0:
        return f"- {resultado['relacion']}: sin huérfanos\n"
    valores = ", ".join(str(v) for v in resultado["valores_huerfanos"])
    return f"- {resultado['relacion']}: {resultado['huerfanos']} huérfano(s) -> {valores}\n"
