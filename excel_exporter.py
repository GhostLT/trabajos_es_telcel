import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import sqlite3
import os
from config import EXPORTS_DIR, DB_PATH
from database import get_db_connection

def apply_header_style(ws, cols):
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    for col_num, col_name in enumerate(cols, 1):
        cell = ws.cell(row=1, column=col_num, value=col_name)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

def export_site_excel(site_id, output_filename=None):
    """
    Generate an As-Built Excel workbook respecting original Telcel sheets and columns
    specifically for a requested site (or all matching).
    """
    if not output_filename:
        output_filename = f"AsBuilt_Tool_{site_id}.xlsx" if site_id else "AsBuilt_Tool_Export.xlsx"
    
    filepath = os.path.join(EXPORTS_DIR, output_filename)
    wb = openpyxl.Workbook()
    
    # Remove default sheet
    default_sheet = wb.active
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Sheet 'Tool' (Dashboard summary replicating original sheet)
    ws_tool = wb.create_sheet(title="Tool")
    ws_tool.views.sheetView[0].showGridLines = True
    
    # Query cell counts
    q_params = (site_id,) if site_id else ()
    where_clause = "WHERE id_name = ?" if site_id else ""
    
    c_gsm_act = cursor.execute(f"SELECT COUNT(*) FROM gsm_cells {where_clause} AND UPPER(activity_status) LIKE '%ACT%'", q_params).fetchone()[0]
    c_gsm_inact = cursor.execute(f"SELECT COUNT(*) FROM gsm_cells {where_clause} AND UPPER(activity_status) NOT LIKE '%ACT%'", q_params).fetchone()[0]
    
    c_umts_act = cursor.execute(f"SELECT COUNT(*) FROM umts_cells {where_clause} AND UPPER(activity_status) LIKE '%ACT%'", q_params).fetchone()[0]
    c_umts_inact = cursor.execute(f"SELECT COUNT(*) FROM umts_cells {where_clause} AND UPPER(activity_status) NOT LIKE '%ACT%'", q_params).fetchone()[0]
    
    c_lte_act = cursor.execute(f"SELECT COUNT(*) FROM lte_cells {where_clause} AND UPPER(activation_status) LIKE '%ACT%'", q_params).fetchone()[0]
    c_lte_inact = cursor.execute(f"SELECT COUNT(*) FROM lte_cells {where_clause} AND UPPER(activation_status) NOT LIKE '%ACT%'", q_params).fetchone()[0]
    
    c_nr_act = cursor.execute(f"SELECT COUNT(*) FROM nr_cells {where_clause} AND UPPER(activation_status) LIKE '%ACT%'", q_params).fetchone()[0]
    c_nr_inact = cursor.execute(f"SELECT COUNT(*) FROM nr_cells {where_clause} AND UPPER(activation_status) NOT LIKE '%ACT%'", q_params).fetchone()[0]

    # Tool sheet headers layout
    ws_tool.cell(row=2, column=1, value="NE ID").font = Font(bold=True)
    ws_tool.cell(row=2, column=2, value=site_id or "TODOS").font = Font(bold=True, color="002060")
    
    ws_tool.cell(row=1, column=9, value="2G").font = Font(bold=True)
    ws_tool.cell(row=1, column=10, value="3G").font = Font(bold=True)
    ws_tool.cell(row=1, column=11, value="4G").font = Font(bold=True)
    ws_tool.cell(row=1, column=12, value="5G").font = Font(bold=True)
    
    ws_tool.cell(row=2, column=8, value="ACTIVES").font = Font(bold=True)
    ws_tool.cell(row=2, column=9, value=c_gsm_act)
    ws_tool.cell(row=2, column=10, value=c_umts_act)
    ws_tool.cell(row=2, column=11, value=c_lte_act)
    ws_tool.cell(row=2, column=12, value=c_nr_act)
    
    ws_tool.cell(row=3, column=8, value="INACTIVOS").font = Font(bold=True)
    ws_tool.cell(row=3, column=9, value=c_gsm_inact)
    ws_tool.cell(row=3, column=10, value=c_umts_inact)
    ws_tool.cell(row=3, column=11, value=c_lte_inact)
    ws_tool.cell(row=3, column=12, value=c_nr_inact)

    # Tool RRU Table
    rru_headers = [
        "Sector", "Modelo de RRUS Final", "Bandas Soportadas", "Tipo",
        "Potencia por RRU", "Número de Serie del Radio", "Tipo de conector RRU",
        "Longitud de FO", "Longitud de DC", "Calibre cable de Fuerza de RRUS"
    ]
    for col_idx, h in enumerate(rru_headers, 1):
        cell = ws_tool.cell(row=6, column=col_idx, value=h)
        cell.fill = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
        cell.font = Font(color="FFFFFF", bold=True)

    rru_rows = cursor.execute(f"""
        SELECT board_name, modelo_rru, bandas_soportadas, blank_col, potencia, no_serie, conector, subrack, aux
        FROM rru_items {where_clause}
    """, q_params).fetchall()
    
    for row_idx, r in enumerate(rru_rows, 7):
        ws_tool.cell(row=row_idx, column=1, value=f"SECTOR {row_idx-6}")
        ws_tool.cell(row=row_idx, column=2, value=r["modelo_rru"])
        ws_tool.cell(row=row_idx, column=3, value=r["bandas_soportadas"])
        ws_tool.cell(row=row_idx, column=4, value=r["board_name"])
        ws_tool.cell(row=row_idx, column=5, value=r["potencia"])
        ws_tool.cell(row=row_idx, column=6, value=r["no_serie"])
        ws_tool.cell(row=row_idx, column=7, value=r["conector"])

    # 2. Sheet 'GSM_CELL_REPORT'
    ws_gsm = wb.create_sheet(title="GSM_CELL_REPORT")
    gsm_cols = [
        "NE Name", "Site Index", "Site Name", "Cell Index", "Cell Name",
        "Activity Status", "CI", "BASEI", "NI", "BCCHNO", "FreqSeg",
        "BLK Status", "Hop HSN", "Hop TSC", "Hop Index", "LAC"
    ]
    apply_header_style(ws_gsm, gsm_cols)
    gsm_records = cursor.execute(f"""
        SELECT ne_name, site_index, site_name, cell_index, cell_name,
               activity_status, ci, basei, ni, bcchno, freq_seg,
               blk_status, hop_hsn, hop_tsc, hop_index, lac
        FROM gsm_cells {where_clause}
    """, q_params).fetchall()
    for row_i, rec in enumerate(gsm_records, 2):
        for col_i, val in enumerate(rec, 1):
            ws_gsm.cell(row=row_i, column=col_i, value=val)

    # 3. Sheet 'UMTS_CELL_REPORT'
    ws_umts = wb.create_sheet(title="UMTS_CELL_REPORT")
    umts_cols = [
        "NE Name", "NodeB ID", "NodeB Name", "Cell ID", "Cell Name",
        "RNC Connection Status", "Activity Status", "BLK Status", "LAC",
        "SAC", "RAC", "Ul Freq", "Dl Freq", "Max Power", "CELLCBSSTATE",
        "CELLMBMSSTATE", "HSDPA OpState", "HSUPA OpState"
    ]
    apply_header_style(ws_umts, umts_cols)
    umts_records = cursor.execute(f"""
        SELECT ne_name, nodeb_id, nodeb_name, cell_id, cell_name,
               rnc_connection_status, activity_status, blk_status, lac,
               sac, rac, ul_freq, dl_freq, max_power, cell_cbs_state,
               cell_mbms_state, hsdpa_opstate, hsupa_opstate
        FROM umts_cells {where_clause}
    """, q_params).fetchall()
    for row_i, rec in enumerate(umts_records, 2):
        for col_i, val in enumerate(rec, 1):
            ws_umts.cell(row=row_i, column=col_i, value=val)

    # 4. Sheet 'LTE_CELL_REPORT'
    ws_lte = wb.create_sheet(title="LTE_CELL_REPORT")
    lte_cols = [
        "Subarea", "RAT", "Operator", "eNodeB ID", "LTE NE Name",
        "eNodeB Function Name", "NE Connection Status", "Cell ID", "Cell Name",
        "Local Cell ID", "TAC", "Frequency Band", "Administrative Status",
        "Activation Status", "Operating Status", "Availability Status"
    ]
    apply_header_style(ws_lte, lte_cols)
    lte_records = cursor.execute(f"""
        SELECT subarea, rat, operator, enodeb_id, lte_ne_name,
               enodeb_function_name, ne_connection_status, cell_id, cell_name,
               local_cell_id, tac, frequency_band, administrative_status,
               activation_status, operating_status, availability_status
        FROM lte_cells {where_clause}
    """, q_params).fetchall()
    for row_i, rec in enumerate(lte_records, 2):
        for col_i, val in enumerate(rec, 1):
            ws_lte.cell(row=row_i, column=col_i, value=val)

    # 5. Sheet 'NR_CELL_REPORT'
    ws_nr = wb.create_sheet(title="NR_CELL_REPORT")
    nr_cols = [
        "Subarea", "RAT", "Operator", "gNodeB ID", "NR NE Name",
        "gNodeB Function Name", "NE Connection Status", "NR Cell ID", "Cell Name",
        "Cell ID", "TAC", "Frequency Band", "Administrative Status",
        "Activation Status", "Operating Status", "Availability Status"
    ]
    apply_header_style(ws_nr, nr_cols)
    nr_records = cursor.execute(f"""
        SELECT subarea, rat, operator, gnodeb_id, nr_ne_name,
               gnodeb_function_name, ne_connection_status, nr_cell_id, cell_name,
               cell_id, tac, frequency_band, administrative_status,
               activation_status, operating_status, availability_status
        FROM nr_cells {where_clause}
    """, q_params).fetchall()
    for row_i, rec in enumerate(nr_records, 2):
        for col_i, val in enumerate(rec, 1):
            ws_nr.cell(row=row_i, column=col_i, value=val)

    # 6. Sheet 'RRU Filtro'
    ws_rru = wb.create_sheet(title="RRU Filtro")
    rru_cols = [
        "NEName", "ID NAME", "Board Name", "Manufacturer Data", "Modelo RRU",
        "Bandas soportadas", "BLANK", "Potencia", "No. serie", "Conector",
        "Subrack", "AUX"
    ]
    apply_header_style(ws_rru, rru_cols)
    rru_all = cursor.execute(f"""
        SELECT ne_name, id_name, board_name, manufacturer_data, modelo_rru,
               bandas_soportadas, blank_col, potencia, no_serie, conector,
               subrack, aux
        FROM rru_items {where_clause}
    """, q_params).fetchall()
    for row_i, rec in enumerate(rru_all, 2):
        for col_i, val in enumerate(rec, 1):
            ws_rru.cell(row=row_i, column=col_i, value=val)

    # 7. Sheet 'Inventory Board'
    ws_inv = wb.create_sheet(title="Inventory Board")
    inv_cols = [
        "NEType", "NEFdn", "NEName", "Wi-Fi Device Info", "AuthenticatorName",
        "Bios Ver", "Bios Ver Ex", "Board Name", "Board Type", "RXU Power Cable Length(m)",
        "CLEICode", "Creditable", "Creditable Changed Time", "Date Of Last Service",
        "Date Of Manufacture", "ExtInfo", "Subrack No.", "Inventory Unit ID",
        "Inventory Unit Type", "Rev(Issue Number)", "PN(BOM Code/Item)", "LAN Ver",
        "Logic Ver", "MBUS Ver", "Manufacturer Data", "Model", "Module No.",
        "Port No.", "Port Type", "Cabinet No.", "SN(Bar Code)", "Slot No.",
        "Slot Pos", "Software Version", "Subslot No.", "Unit Position", "User Label",
        "Vendor Name", "Vendor Unit Family Type", "Vendor Unit Type Number", "Hardware Version"
    ]
    apply_header_style(ws_inv, inv_cols)
    # If exporting a specific site, grab site's inventory; if exporting all, limit to top 5000 to prevent timeout
    limit_clause = "" if site_id else "LIMIT 5000"
    inv_records = cursor.execute(f"""
        SELECT ne_type, ne_fdn, ne_name, wifi_device_info, authenticator_name,
               bios_ver, bios_ver_ex, board_name, board_type, rxu_power_cable_length,
               clei_code, creditable, creditable_changed_time, date_of_last_service,
               date_of_manufacture, ext_info, subrack_no, inventory_unit_id,
               inventory_unit_type, rev_issue_number, pn_bom_code, lan_ver,
               logic_ver, mbus_ver, manufacturer_data, model, module_no,
               port_no, port_type, cabinet_no, sn_barcode, slot_no,
               slot_pos, software_version, subslot_no, unit_position, user_label,
               vendor_name, vendor_unit_family_type, vendor_unit_type_number, hardware_version
        FROM inventory_boards {where_clause} {limit_clause}
    """, q_params).fetchall()
    for row_i, rec in enumerate(inv_records, 2):
        for col_i, val in enumerate(rec, 1):
            ws_inv.cell(row=row_i, column=col_i, value=val)

    # 8. Sheet 'RRU Data Base'
    ws_db = wb.create_sheet(title="RRU Data Base")
    db_cols = ["Radio", "Bandas Soportadas", "Potencia", "Conector"]
    apply_header_style(ws_db, db_cols)
    db_records = cursor.execute("SELECT radio, bandas_soportadas, potencia, conector FROM rru_catalog").fetchall()
    for row_i, rec in enumerate(db_records, 2):
        for col_i, val in enumerate(rec, 1):
            ws_db.cell(row=row_i, column=col_i, value=val)

    # Remove the initial default empty sheet
    if default_sheet in wb.worksheets:
        wb.remove(default_sheet)
        
    wb.save(filepath)
    conn.close()
    return filepath
