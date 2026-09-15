# Trabajos ES Telcel - Sistema Web As-Built & Pipeline de Automatización

Plataforma integral de ingeniería para la gestión, procesamiento y automatización de entregables **As-Built** y **OTAS X REFS** de estaciones base celulares (**2G GSM, 3G UMTS, 4G LTE, 5G NR**) e inventario de hardware para **Telcel**.

El sistema procesa y cruza información proveniente de múltiples fuentes (archivos de ingeniería de ~250 MB con 1.5 millones de registros, listas de materiales, planos CAD, evidencia fotográfica ISDP Smart QC y auditoría de cambios) eliminando la lentitud y bloqueos de Excel mediante una base de datos **SQLite indexada** con interfaz moderna en **Bootstrap 5** y **Python (Flask)**.

---

## Flujo de Trabajo Secuencial (Pipeline de Automatización)

A partir del análisis detallado de los videos de capacitación técnica del proceso de modernización Telcel (E&S / Huawei / Telcel), se ha estructurado la aplicación en **5 Fases Secuenciales Automatizadas**:

```
[Insumos de Entrada] ──► [Motor de Reglas] ──► [Generador OTAS X REFS] ──► [Generador AS BUILT] ──► [Control & Tracker]
   • AsBuilt Tool           • Type Site             • Propuesta (Rev A)         • Ejecución Pasada       • Diff Celda a Celda
   • OTA Validada           • 8 AWG vs 7 AWG        • Croquis Gabinete FPP      • Referencias Fotos      • TRACKER EYS
   • Material List (ML)     • Metrajes DC / FO                                    (Ver foto 10, 11, 17)
   • AutoCAD (DWG)          • Sectores & Azimuts
   • ISDP Smart QC
```

### Paso 1: Ingesta y Cruce de Insumos por Sitio
Al introducir el código del sitio (`ID NAME` / `Short DU ID`, ej. **`CA0249`**, **`QR5094`**, **`JL4089`**), el sistema extrae automáticamente:
1. **As-Built Tool (Base de Datos)**: Conteo y estado de celdas 2G, 3G, 4G y 5G, tarjetas BBU y radios RRU.
2. **OTA Validada (Versión previa aprobada)**: Existencia y altura de GPS (ej. 15.0 m), gabinete base (`TP48200A`), rectificadores y comentarios previos de ingeniería.
3. **Material List (ML / Lista de Materiales)**:
   - Tiradas de fibra óptica (ej. 40.0 m) y cable de fuerza DC (ej. 38.0 m).
   - Longitud y conectores de jumpers (ej. 2.0 m con conectores DIN a 4.3-10 y 4.3-10 a 4.3-10).
4. **AutoCAD (DWG)**: Azimuts de sectores (ej. ALFA: 350°, BETA: 130°, GAMMA: 250°) y alturas de montaje (15.0 m).
5. **ISDP Smart QC (Huawei Cloud)**: Números de serie reales leídos de las fotos de etiquetas de antenas (`MBMF-65-18DDE-IN-43`, `ADU4518R6v06`, etc.) y radios RRU (`RRU5526`, `RRU5527et`).

---

### Paso 2: Motor de Reglas de Cableado y Metrajes Automáticos
El sistema aplica automáticamente la matriz de compatibilidad técnica entre modelos de radio y calibres de cable de fuerza:

| Calibre de Cable | Diámetro | Modelos de Radio Compatibles | Banda | Cálculo de Metraje |
| :---: | :---: | :--- | :---: | :--- |
| **8 AWG** | 8 mm | `RRU5513`, `RRU5526`, `RRU5526w`, `AAU 5G` | 850 / 600 MHz | \(3\text{ tiradas} \times 38\text{ m} = 114\text{ m}\) |
| **7 AWG** | 10 mm | `RRU5517`, `RRU5527`, `RRU5527et` (Tribanda) | 1900 / 2100 / 2600 MHz | \(3\text{ tiradas} \times 38\text{ m} = 114\text{ m}\) |
| **10 AWG** | 6 mm | Celdas legadas / Micro RRU | - | 0 m |
| **5 / 4 AWG** | 16 / 25 mm | Alimentación principal Planta &rarr; DCDU | - | Según diseño |

*Validación cruzada*: La suma de metrajes debe coincidir exactamente en la carátula (`ADICIONALES HARDWARE RF`), en la tabla de sectores y en la lista de materiales (ML).

---

### Paso 3: Generador Oficial `OTAS X REFS` (Revisión A)
- **Nomenclatura**: Todo nuevo documento arranca en **`REV A`** (solo cambia a REV B, C... ante un rechazo del cliente).
- **Redacción de Propuesta**: Redacta los requerimientos técnicos en tiempo futuro:
  - *"Se requiere reutilizar gabinete TP48200A..."*
  - *"Se requiere suministro e instalación de equipos (1) BBU5900, (2) DCDU17E y tarjetería (2) UBBPg2..."*
  - *"Se requieren 6 tiradas de Fibra de 40.0m y 6 tiradas de cable DC de 38.0m..."*
- **Distribución de Gabinete FPP**: Asignación de rectificadores (`PSU-2U`) y tarjetas banda base (`UBBPg2`, `UMPTe2`).

---

### Paso 4: Generador Oficial `ESTADO FINAL DE SITIO / AS BUILT`
Transformación automática de la propuesta a ejecución real:
1. **Conjugación al Pasado**:
   - De *"Se requiere instalar..."* a *"Se instaló / Se reutilizó / Se desmontó..."*.
2. **Inyección de Referencias Fotográficas ISDP**:
   - Cada renglón de instalación incluye la cita a la foto de campo correspondiente:
     - *"Se instalaron 3 RRU 5526 back to back... Ver foto 10 de sectores Alpha, Beta y Gamma."*
     - *"Se instalaron 3 RRU5527et back to back... Ver foto 17 de sectores Alpha, Beta y Gamma."*
     - *"Se reutilizaron 2 antenas MBMF-65-18DDE-IN-43... Ver foto 11 de sectores Alpha y Gamma."*
3. **Desmontajes Detallados**:
   - Identificación automática de antenas y radios desmontados para liberar espacio en torre (U850, GU1900, L2100, L2600, antenas TENPOLE y QUADPOLE).

---

### Paso 5: Auditoría de Control de Cambios & TRACKER EYS
1. **Control de Cambios Celda por Celda**:
   - Matriz comparativa entre **`OTA Validada`** (versión anterior) vs **`OTAS REFS`** (nueva propuesta).
   - Detección visual de discrepancias en fechas, modelos de antena, longitudes de jumpers y calibres de cable.
2. **Integración con TRACKER EYS**:
   - Registro automático del sitio en el tablero de control:
     - `Service`: As built / New Template
     - `OTAS Status`: Completed (100%)
     - `Team Owner`: ENGINEERING AND SERVICES JF SA DE CV
     - `ITEM DESCRIPTION`: WITH TOOL
     - `PRECIO`: $ 249.16 MXN

---

## Módulos de la Aplicación Web

1. **`/pipeline` (Flujo Automatizado Secuencial)**:
   - Asistente visual e interactivo de 5 pasos que guía y automatiza el proceso de cada sitio.
2. **`/` (Dashboard As-Built Tool)**:
   - Consulta instantánea de celdas activas e inactivas (2G, 3G, 4G, 5G), sectores y radios RRU.
3. **`/cells` (Explorador Global de Celdas)**:
   - Búsqueda y filtrado por celda, ID de sitio, estado y tecnología con paginación optimizada.
4. **`/inventory` (Inventario de Tarjetas & RRU)**:
   - Búsqueda por número de serie (SN Barcode), modelo de tarjeta (BBU, DCDU) o módulo de radio.
5. **`/import-export` (Gestión y Descargas Excel)**:
   - Sincronización en segundo plano con el archivo maestro y descarga de libros Excel (.xlsx) estructurados.

---

## Estructura de Archivos del Proyecto

```
C:\proyectos\trabajos_es_telcel\
├── app.py                      # Servidor Flask, rutas REST y endpoints del pipeline
├── config.py                   # Rutas y configuración general
├── database.py                 # Esquema SQLite, tablas indexadas y conexiones
├── etl_importer.py             # Motor de streaming por lotes (Excel -> SQLite)
├── excel_exporter.py           # Generador de archivos Excel oficiales (.xlsx)
├── requirements.txt            # Dependencias del proyecto
├── README.md                   # Documentación técnica completa
├── .gitignore                  # Exclusión de base de datos pesada y temporales
├── static/
│   ├── css/custom.css          # Estilos corporativos Telcel y badges
│   └── js/app.js               # Interactividad y mayúsculas automáticas
└── templates/
    ├── base.html               # Layout maestro con navbar
    ├── pipeline.html           # Vista del Flujo Automatizado Secuencial
    ├── index.html              # Dashboard As-Built Tool
    ├── cells.html              # Explorador paginado de celdas
    ├── inventory.html          # Explorador de hardware y seriales
    └── import_export.html      # Panel de sincronización y descargas
```

---

## Instrucciones para Ejecutar

1. **Instalar dependencias**:
   ```powershell
   cd C:\proyectos\trabajos_es_telcel
   pip install -r requirements.txt
   ```

2. **Iniciar la aplicación**:
   ```powershell
   python app.py
   ```

3. **Abrir en el navegador**:
   - Portal General: [http://localhost:5000](http://localhost:5000)
   - Flujo Automatizado: [http://localhost:5000/pipeline](http://localhost:5000/pipeline)

---

## Repositorio en GitHub

* **URL del Repositorio:** [https://github.com/GhostLT/trabajos_es_telcel](https://github.com/GhostLT/trabajos_es_telcel)
* **Rama principal:** `main`
