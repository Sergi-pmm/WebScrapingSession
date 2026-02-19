import requests
import pandas as pd


def descargar_tabla_ine_json(id_tabla, nult=None, tip=None, filtros=None):
    base = 'https://servicios.ine.es/wstempus/js/ES'
    params = {}
    if nult:
        params['nult'] = nult
    if tip:
        params['tip'] = tip
    if filtros:
        params['tv'] = filtros

    r = requests.get(f'{base}/DATOS_TABLA/{id_tabla}', params=params)
    r.raise_for_status()
    datos = r.json()

    filas = []
    for serie in datos:
        for d in serie.get('Data', []):
            filas.append({
                'serie': serie['Nombre'].strip(),
                'codigo': serie['COD'],
                'periodo': d['FK_Periodo'],
                'anyo': d['Anyo'],
                'valor': d['Valor']
            })

    return pd.DataFrame(filas)


if __name__ == '__main__':
    df = descargar_tabla_ine_json(50902, nult=3)
    print(f'{len(df)} filas descargadas')
    df.to_csv('ipc_datos.csv', index=False, sep=';')
    print(f'Guardado ipc_datos.csv con {len(df)} filas')