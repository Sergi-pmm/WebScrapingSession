#!/usr/bin/env python3
"""
CLI para consultar la API del INE (Instituto Nacional de Estadística).

Uso:
    python ine_cli.py operaciones              # Lista todas las operaciones
    python ine_cli.py operaciones -b "IPC"     # Busca operaciones por nombre
    python ine_cli.py tablas 25               # Tablas de la operación con Id=25
    python ine_cli.py datos 76092             # Descarga datos de tabla 76092
    python ine_cli.py datos 76092 -o ipc.csv  # Exporta a CSV
"""

import argparse
import sys
from datetime import datetime

import pandas as pd
import requests

BASE_URL = "https://servicios.ine.es/wstempus/js/ES"
TIMEOUT = 30


# ─────────────────────────────────────────────────────────────────────────────
# Funciones de acceso a la API
# ─────────────────────────────────────────────────────────────────────────────

def fetch_json(endpoint: str) -> list | dict:
    """Obtiene JSON desde un endpoint de la API del INE."""
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def get_operaciones() -> pd.DataFrame:
    """Devuelve DataFrame con todas las operaciones disponibles."""
    data = fetch_json("OPERACIONES_DISPONIBLES")
    return pd.DataFrame(data)[["Id", "Codigo", "Nombre"]]


def get_tablas(id_operacion: int) -> pd.DataFrame:
    """Devuelve DataFrame con las tablas de una operación."""
    data = fetch_json(f"TABLAS_OPERACION/{id_operacion}")
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)[["Id", "Nombre", "Anyo_Periodo_Ini", "Anyo_Periodo_Fin"]]


def get_datos_tabla(id_tabla: int) -> pd.DataFrame:
    """Descarga y aplana los datos de una tabla."""
    raw = fetch_json(f"DATOS_TABLA/{id_tabla}")
    if not raw:
        return pd.DataFrame()
    
    df_series = pd.DataFrame(raw)
    df_long = df_series.explode("Data")
    
    # Separar metadatos de valores
    cols_meta = [c for c in df_series.columns if c != "Data"]
    df_meta = df_long[cols_meta].reset_index(drop=True)
    df_values = pd.json_normalize(df_long["Data"]).reset_index(drop=True)
    
    df = pd.concat([df_meta, df_values], axis=1)
    
    # Convertir fecha de timestamp a datetime
    if "Fecha" in df.columns:
        df["Fecha"] = pd.to_datetime(df["Fecha"], unit="ms", errors="coerce")
    
    # Asegurar Valor numérico
    if "Valor" in df.columns:
        df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    
    return df


# ─────────────────────────────────────────────────────────────────────────────
# Comandos CLI
# ─────────────────────────────────────────────────────────────────────────────

def cmd_operaciones(args):
    """Muestra operaciones disponibles, con filtro opcional."""
    df = get_operaciones()
    
    if args.buscar:
        mask = df["Nombre"].str.contains(args.buscar, case=False, na=False)
        df = df[mask]
    
    if df.empty:
        print("No se encontraron operaciones.")
        return
    
    print(f"\n{'Id':>6}  {'Código':<12}  Nombre")
    print("-" * 80)
    for _, row in df.iterrows():
        nombre = row["Nombre"][:55] + "..." if len(row["Nombre"]) > 58 else row["Nombre"]
        print(f"{row['Id']:>6}  {row['Codigo']:<12}  {nombre}")
    print(f"\nTotal: {len(df)} operaciones")


def cmd_tablas(args):
    """Muestra las tablas de una operación."""
    df = get_tablas(args.id_operacion)
    
    if df.empty:
        print(f"No se encontraron tablas para la operación {args.id_operacion}.")
        return
    
    print(f"\n{'Id':>8}  {'Periodo':<15}  Nombre")
    print("-" * 90)
    for _, row in df.iterrows():
        periodo = f"{row['Anyo_Periodo_Ini']}-{row['Anyo_Periodo_Fin']}"
        nombre = row["Nombre"][:60] + "..." if len(row["Nombre"]) > 63 else row["Nombre"]
        print(f"{row['Id']:>8}  {periodo:<15}  {nombre}")
    print(f"\nTotal: {len(df)} tablas")


def cmd_datos(args):
    """Descarga datos de una tabla y opcionalmente exporta a CSV."""
    print(f"Descargando tabla {args.id_tabla}...")
    df = get_datos_tabla(args.id_tabla)
    
    if df.empty:
        print("No se obtuvieron datos.")
        return
    
    # Mostrar resumen
    print(f"\nRegistros: {len(df)}")
    print(f"Columnas: {', '.join(df.columns)}")
    
    if "Nombre" in df.columns:
        series_unicas = df["Nombre"].nunique()
        print(f"Series únicas: {series_unicas}")
    
    if "Fecha" in df.columns:
        print(f"Rango temporal: {df['Fecha'].min()} → {df['Fecha'].max()}")
    
    # Vista previa
    print("\nVista previa (últimos 5 registros):")
    cols_vista = [c for c in ["Nombre", "Fecha", "Valor"] if c in df.columns]
    print(df[cols_vista].head().to_string(index=False))
    
    # Exportar si se indica
    if args.output:
        df.to_csv(args.output, index=False)
        print(f"\n✓ Exportado a {args.output}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="CLI para consultar la API del INE",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s operaciones              Lista todas las operaciones
  %(prog)s operaciones -b "IPC"     Busca operaciones que contengan "IPC"
  %(prog)s tablas 25               Muestra tablas de la operación 25
  %(prog)s datos 76092             Descarga la tabla 76092
  %(prog)s datos 76092 -o ipc.csv  Descarga y exporta a CSV
        """
    )
    subparsers = parser.add_subparsers(dest="comando", required=True)
    
    # Subcomando: operaciones
    p_ops = subparsers.add_parser("operaciones", help="Lista operaciones disponibles")
    p_ops.add_argument("-b", "--buscar", help="Filtrar por texto en el nombre")
    p_ops.set_defaults(func=cmd_operaciones)
    
    # Subcomando: tablas
    p_tablas = subparsers.add_parser("tablas", help="Lista tablas de una operación")
    p_tablas.add_argument("id_operacion", type=int, help="Id de la operación")
    p_tablas.set_defaults(func=cmd_tablas)
    
    # Subcomando: datos
    p_datos = subparsers.add_parser("datos", help="Descarga datos de una tabla")
    p_datos.add_argument("id_tabla", type=int, help="Id de la tabla")
    p_datos.add_argument("-o", "--output", help="Exportar a fichero CSV")
    p_datos.set_defaults(func=cmd_datos)
    
    args = parser.parse_args()
    
    try:
        args.func(args)
    except requests.RequestException as e:
        print(f"Error de conexión: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
