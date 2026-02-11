# Taller de Web Scraping con Python

En este **Taller de Web Scraping con Python** se presentan los fundamentos de Python, desde el propio lenguaje hasta la extracción y análisis de datos web.

Este repositorio contiene notebooks, scripts y material complementario para el proceso de scraping y manipulación de datos.

---

## Objetivos y contenido

- Fundamentos de Python y Pandas  
- Uso de `requests` y `BeautifulSoup` para extraer datos web  
- Técnicas para limpiar y analizar datos con Pandas  
- Buenas prácticas y consideraciones legales en web scraping  

---

## Estructura del Taller

**notebooks/** → Notebooks interactivos en Jupyter:

- `01_fundamentos_python.ipynb`
- `02_fundamentos_pandas.ipynb`
- `03_web_scraping_basico.ipynb`

**slides/** → Presentación y materiales en PDF utilizados en el taller.

---

## Requisitos

- Python 3.x  
- Miniconda  

---

## Entorno de trabajo con Miniconda

### 1. Clonar el repositorio

```
$ git clone https://github.com/Sergi-pmm/WebScrapingSession.git
$ cd WebScrapingSession
```

### 2. Crear y activar entorno

macOS / Linux

```
$ conda create -n scraping-env python=3.11
$ conda activate scraping-env
```

Windows (Anaconda Prompt)

```
> conda create -n scraping-env python=3.11
> conda activate scraping-env
```

### 3. Instalar dependencias

```
$ pip install -r requirements.txt
```

### 4. Ejecutar JupyterLab

```
$ jupyter lab
```

### Verificación opcional

```
$ python --version
$ conda info --envs
```
---

## Contacto y Créditos

Material desarrollado por [Sergi Pons](https://es.linkedin.com/in/sergi-pons-muñoz-de-morales-b1712b47) para un taller introductorio impartido en la Universitat de Barcelona Business School.

Si tienes dudas o sugerencias, puedes abrir un **issue** en el repositorio.