import sqlite3
import os
from config import DB_PATH

def get_db_connection():
    """Create and return a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn

def init_db():
    """Initialize database tables and indexes."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. GSM (2G) Cells
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gsm_cells (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_name TEXT,
        ne_name TEXT,
        site_index TEXT,
        site_name TEXT,
        cell_index TEXT,
        cell_name TEXT,
        activity_status TEXT,
        ci TEXT,
        basei TEXT,
        ni TEXT,
        bcchno TEXT,
        freq_seg TEXT,
        blk_status TEXT,
        hop_hsn TEXT,
        hop_tsc TEXT,
        hop_index TEXT,
        lac TEXT
    );
    """)

    # 2. UMTS (3G) Cells
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS umts_cells (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_name TEXT,
        ne_name TEXT,
        nodeb_id TEXT,
        nodeb_name TEXT,
        cell_id TEXT,
        cell_name TEXT,
        rnc_connection_status TEXT,
        activity_status TEXT,
        blk_status TEXT,
        lac TEXT,
        sac TEXT,
        rac TEXT,
        ul_freq TEXT,
        dl_freq TEXT,
        max_power TEXT,
        cell_cbs_state TEXT,
        cell_mbms_state TEXT,
        hsdpa_opstate TEXT,
        hsupa_opstate TEXT
    );
    """)

    # 3. LTE (4G) Cells
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lte_cells (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_name TEXT,
        subarea TEXT,
        rat TEXT,
        operator TEXT,
        enodeb_id TEXT,
        lte_ne_name TEXT,
        enodeb_function_name TEXT,
        ne_connection_status TEXT,
        cell_id TEXT,
        cell_name TEXT,
        local_cell_id TEXT,
        tac TEXT,
        frequency_band TEXT,
        administrative_status TEXT,
        activation_status TEXT,
        operating_status TEXT,
        availability_status TEXT
    );
    """)

    # 4. NR (5G) Cells
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nr_cells (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_name TEXT,
        subarea TEXT,
        rat TEXT,
        operator TEXT,
        gnodeb_id TEXT,
        nr_ne_name TEXT,
        gnodeb_function_name TEXT,
        ne_connection_status TEXT,
        nr_cell_id TEXT,
        cell_name TEXT,
        cell_id TEXT,
        tac TEXT,
        frequency_band TEXT,
        administrative_status TEXT,
        activation_status TEXT,
        operating_status TEXT,
        availability_status TEXT
    );
    """)

    # 5. Inventory Board (Hardware Cards)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory_boards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_name TEXT,
        ne_type TEXT,
        ne_fdn TEXT,
        ne_name TEXT,
        wifi_device_info TEXT,
        authenticator_name TEXT,
        bios_ver TEXT,
        bios_ver_ex TEXT,
        board_name TEXT,
        board_type TEXT,
        rxu_power_cable_length TEXT,
        clei_code TEXT,
        creditable TEXT,
        creditable_changed_time TEXT,
        date_of_last_service TEXT,
        date_of_manufacture TEXT,
        ext_info TEXT,
        subrack_no TEXT,
        inventory_unit_id TEXT,
        inventory_unit_type TEXT,
        rev_issue_number TEXT,
        pn_bom_code TEXT,
        lan_ver TEXT,
        logic_ver TEXT,
        mbus_ver TEXT,
        manufacturer_data TEXT,
        model TEXT,
        module_no TEXT,
        port_no TEXT,
        port_type TEXT,
        cabinet_no TEXT,
        sn_barcode TEXT,
        slot_no TEXT,
        slot_pos TEXT,
        software_version TEXT,
        subslot_no TEXT,
        unit_position TEXT,
        user_label TEXT,
        vendor_name TEXT,
        vendor_unit_family_type TEXT,
        vendor_unit_type_number TEXT,
        hardware_version TEXT
    );
    """)

    # 6. RRU Items
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rru_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ne_name TEXT,
        id_name TEXT,
        board_name TEXT,
        manufacturer_data TEXT,
        modelo_rru TEXT,
        bandas_soportadas TEXT,
        blank_col TEXT,
        potencia TEXT,
        no_serie TEXT,
        conector TEXT,
        subrack TEXT,
        aux TEXT
    );
    """)

    # 7. RRU Catalog
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rru_catalog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        radio TEXT,
        bandas_soportadas TEXT,
        potencia TEXT,
        conector TEXT
    );
    """)

    # 8. Import Metadata & Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS import_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_file TEXT,
        started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        completed_at DATETIME,
        status TEXT,
        records_summary TEXT
    );
    """)

    # Create Indexes for lightning fast queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_gsm_id_name ON gsm_cells(id_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_gsm_cell_name ON gsm_cells(cell_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_gsm_activity ON gsm_cells(activity_status);")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_umts_id_name ON umts_cells(id_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_umts_cell_name ON umts_cells(cell_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_umts_activity ON umts_cells(activity_status);")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lte_id_name ON lte_cells(id_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lte_cell_name ON lte_cells(cell_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lte_band ON lte_cells(frequency_band);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lte_activity ON lte_cells(activation_status);")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nr_id_name ON nr_cells(id_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nr_cell_name ON nr_cells(cell_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nr_band ON nr_cells(frequency_band);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nr_activity ON nr_cells(activation_status);")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_id_name ON inventory_boards(id_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_ne_name ON inventory_boards(ne_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_sn ON inventory_boards(sn_barcode);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_board ON inventory_boards(board_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_model ON inventory_boards(model);")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rru_id_name ON rru_items(id_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rru_sn ON rru_items(no_serie);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rru_model ON rru_items(modelo_rru);")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
