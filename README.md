# Trabajos ES Telcel - Sistema Web As-Built

Plataforma web de ingeniería para la gestión, consulta de alta velocidad y exportación de información técnica de celdas celulares (**2G GSM, 3G UMTS, 4G LTE, 5G NR**) e inventario de hardware de estaciones base de **Telcel**.

El proyecto resuelve la lentitud y bloqueos causados por el manejo de libros de Excel de gran tamaño (~250 MB y más de 1.5 millones de registros), trasladando la información a una base de datos **SQLite indexada** con una interfaz responsiva desarrollada en **Bootstrap 5** y **Python (Flask)**.

---

## Características Principales

1. **Herramienta As-Built Interactiva (Dashboard Tool)**:
   - Consulta instantánea por Sitio / `NE ID` (ej. `CA0249`, `JL4089`, `MI2742`, `JL1999`, `MI2888`).
   - Resumen en tiempo real de celdas **Activas** e **Inactivas** desglosadas por tecnología (2G, 3G, 4G, 5G).
   - Tabla de módulos de radio **RRU** y asignación de sectores (Modelo RRU, Bandas, Potencia, Conector, Número de Serie).
   - Pestañas con el detalle completo de celdas por tecnología e inventario de tarjetas de hardware.

2. **Explorador Global de Celdas**:
   - Navegación paginada por tecnología: 4G LTE, 3G UMTS, 2G GSM y 5G NR.
   - Filtros por nombre de celda, código de sitio y estado de actividad/activación.

3. **Explorador de Inventario y Hardware**:
   - Búsqueda en tiempo real por **Número de Serie (SN / Barcode)**, Modelo de Tarjeta (BBU, DCDU, MRRU), Slot o Sitio.

4. **Integridad del Archivo Excel Original**:
   - El archivo maestro original de 250 MB (`AsBuilt Tool...xlsx`) permanece protegido en modo de **sólo lectura** (`read-only`).
   - Motor ETL por lotes (streaming) con `openpyxl` que alimenta la base de datos sin sobrecargar la memoria RAM.

5. **Descarga y Exportación Fiel a Excel**:
   - Botón de **"Descargar en Excel"** que genera al vuelo un archivo `.xlsx` estructurado con los mismos nombres de hojas y columnas que el formato oficial:
     - `Tool` (Hoja resumen idéntica a la plantilla de ingeniería)
     - `GSM_CELL_REPORT` (16 columnas)
     - `UMTS_CELL_REPORT` (18 columnas)
     - `LTE_CELL_REPORT` (16 columnas)
     - `NR_CELL_REPORT` (16 columnas)
     - `RRU Filtro` (12 columnas)
     - `Inventory Board` (41 columnas)
     - `RRU Data Base` (4 columnas)

---

## Estructura del Proyecto

```
C:\proyectos\trabajos_es_telcel\
├── app.py                      # Servidor web Flask y endpoints REST
├── config.py                   # Configuración de rutas y variables de entorno
├── database.py                 # Conexión SQLite, esquemas y creación de índices
├── etl_importer.py             # Script de streaming ETL (Excel -> SQLite)
├── excel_exporter.py           # Generador de reportes Excel (.xlsx) oficiales
├── requirements.txt            # Dependencias del proyecto
├── README.md                   # Documentación del sistema
├── .gitignore                  # Exclusión de archivos binarios grandes y cachés
├── static/
│   ├── css/
│   │   └── custom.css          # Estilos personalizados Telcel
│   └── js/
│       └── app.js              # Funciones interactivas de interfaz
└── templates/
    ├── base.html               # Layout maestro Bootstrap 5 con barra superior
    ├── index.html              # Dashboard As-Built y buscador de sitios
    ├── cells.html              # Explorador paginado de celdas
    ├── inventory.html          # Explorador de tarjetas e inventario RRU
    └── import_export.html      # Panel de sincronización y descargas
```

---

## Base de Datos (SQLite)

La base de datos `database.db` almacena las tablas relacionales con índices B-Tree optimizados:

- **`gsm_cells`**: Celdas 2G con índices en `id_name`, `cell_name`, `activity_status`.
- **`umts_cells`**: Celdas 3G con índices en `id_name`, `cell_name`, `activity_status`.
- **`lte_cells`**: Celdas 4G con índices en `id_name`, `cell_name`, `frequency_band`, `activation_status`.
- **`nr_cells`**: Celdas 5G con índices en `id_name`, `cell_name`, `frequency_band`, `activation_status`.
- **`inventory_boards`**: Inventario de tarjetas (590k+ registros) con índices en `id_name`, `sn_barcode`, `board_name`, `model`.
- **`rru_items`**: Radios RRU por sitio con índices en `id_name`, `no_serie`, `modelo_rru`.
- **`rru_catalog`**: Catálogo de especificaciones técnicas de radios.
- **`import_metadata`**: Historial de ingestas y marcas de tiempo.

---

## Instalación y Ejecución

### 1. Requisitos Previos
Tener instalado Python 3.9 o superior. Las librerías necesarias se encuentran en `requirements.txt`:
```bash
cd C:\proyectos\trabajos_es_telcel
pip install -r requirements.txt
```

### 2. Inicializar Base de Datos e Importar Datos
Puedes inicializar la base de datos y cargar la información ejecutando el importador ETL:
```bash
python etl_importer.py
```
*(También puedes iniciar la sincronización desde el botón interactivo en la pestaña "Importar / Descargar Excel" de la aplicación web).*

### 3. Iniciar el Servidor Web
Ejecuta la aplicación Flask:
```bash
python app.py
```

Abre tu navegador web e ingresa a:
```
http://localhost:5000
```

---

## Subir a GitHub

El proyecto ya cuenta con el repositorio local de Git configurado con `.gitignore` para proteger la privacidad y evitar subir archivos binarios pesados.

Para vincularlo a tu repositorio remoto de GitHub y subir los cambios:

```bash
cd C:\proyectos\trabajos_es_telcel

# 1. Agregar el repositorio remoto de tu cuenta de GitHub:
git remote add origin https://github.com/TU_USUARIO/trabajos_es_telcel.git

# 2. Renombrar la rama principal a main (o master según tu preferencia):
git branch -M main

# 3. Subir el código:
git push -u origin main
```
