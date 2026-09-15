from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
import os
import threading
import time
from config import BASE_DIR, DB_PATH, EXCEL_SOURCE_PATH, EXPORTS_DIR, SECRET_KEY, PORT, DEBUG
from database import init_db, get_db_connection
from etl_importer import run_full_etl
from excel_exporter import export_site_excel

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Background ETL state
etl_state = {
    "running": False,
    "progress": "",
    "summary": None,
    "error": None
}

@app.before_request
def setup_on_first_request():
    if not os.path.exists(DB_PATH):
        init_db()

@app.route("/")
def index():
    site_query = request.args.get("site", "").strip().upper()
    conn = get_db_connection()
    cursor = conn.cursor()

    # System overview counts
    try:
        total_gsm = cursor.execute("SELECT COUNT(*) FROM gsm_cells").fetchone()[0]
        total_umts = cursor.execute("SELECT COUNT(*) FROM umts_cells").fetchone()[0]
        total_lte = cursor.execute("SELECT COUNT(*) FROM lte_cells").fetchone()[0]
        total_nr = cursor.execute("SELECT COUNT(*) FROM nr_cells").fetchone()[0]
        total_inv = cursor.execute("SELECT COUNT(*) FROM inventory_boards").fetchone()[0]
        total_rru = cursor.execute("SELECT COUNT(*) FROM rru_items").fetchone()[0]
    except Exception:
        total_gsm = total_umts = total_lte = total_nr = total_inv = total_rru = 0

    site_data = None
    if site_query:
        # Search by ID Name or partial match
        # 1. GSM
        gsm_cells = cursor.execute("""
            SELECT * FROM gsm_cells WHERE id_name = ? OR ne_name LIKE ? OR site_name LIKE ?
        """, (site_query, f"%{site_query}%", f"%{site_query}%")).fetchall()

        # 2. UMTS
        umts_cells = cursor.execute("""
            SELECT * FROM umts_cells WHERE id_name = ? OR ne_name LIKE ? OR nodeb_name LIKE ?
        """, (site_query, f"%{site_query}%", f"%{site_query}%")).fetchall()

        # 3. LTE
        lte_cells = cursor.execute("""
            SELECT * FROM lte_cells WHERE id_name = ? OR lte_ne_name LIKE ? OR cell_name LIKE ?
        """, (site_query, f"%{site_query}%", f"%{site_query}%")).fetchall()

        # 4. NR
        nr_cells = cursor.execute("""
            SELECT * FROM nr_cells WHERE id_name = ? OR nr_ne_name LIKE ? OR cell_name LIKE ?
        """, (site_query, f"%{site_query}%", f"%{site_query}%")).fetchall()

        # 5. RRU items
        rru_list = cursor.execute("""
            SELECT * FROM rru_items WHERE id_name = ? OR ne_name LIKE ?
        """, (site_query, f"%{site_query}%")).fetchall()

        # 6. Inventory boards
        inv_list = cursor.execute("""
            SELECT * FROM inventory_boards WHERE id_name = ? OR ne_name LIKE ? LIMIT 100
        """, (site_query, f"%{site_query}%")).fetchall()

        # Count active/inactives
        gsm_act = sum(1 for c in gsm_cells if "ACT" in (c["activity_status"] or "").upper())
        gsm_inact = len(gsm_cells) - gsm_act

        umts_act = sum(1 for c in umts_cells if "ACT" in (c["activity_status"] or "").upper())
        umts_inact = len(umts_cells) - umts_act

        lte_act = sum(1 for c in lte_cells if "ACT" in (c["activation_status"] or "").upper())
        lte_inact = len(lte_cells) - lte_act

        nr_act = sum(1 for c in nr_cells if "ACT" in (c["activation_status"] or "").upper())
        nr_inact = len(nr_cells) - nr_act

        site_data = {
            "site_id": site_query,
            "counts": {
                "gsm": {"act": gsm_act, "inact": gsm_inact, "total": len(gsm_cells)},
                "umts": {"act": umts_act, "inact": umts_inact, "total": len(umts_cells)},
                "lte": {"act": lte_act, "inact": lte_inact, "total": len(lte_cells)},
                "nr": {"act": nr_act, "inact": nr_inact, "total": len(nr_cells)},
            },
            "gsm_cells": [dict(c) for c in gsm_cells],
            "umts_cells": [dict(c) for c in umts_cells],
            "lte_cells": [dict(c) for c in lte_cells],
            "nr_cells": [dict(c) for c in nr_cells],
            "rru_list": [dict(r) for r in rru_list],
            "inv_list": [dict(i) for i in inv_list]
        }

    conn.close()
    return render_template(
        "index.html",
        site_query=site_query,
        site_data=site_data,
        stats={
            "gsm": total_gsm,
            "umts": total_umts,
            "lte": total_lte,
            "nr": total_nr,
            "inv": total_inv,
            "rru": total_rru
        }
    )

@app.route("/pipeline")
def pipeline():
    site_query = request.args.get("site", "CA0249").strip().upper()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    gsm_cells = cursor.execute("SELECT * FROM gsm_cells WHERE id_name = ?", (site_query,)).fetchall()
    gsm_act = sum(1 for c in gsm_cells if "ACT" in (c["activity_status"] or "").upper())
    gsm_inact = len(gsm_cells) - gsm_act
    
    umts_cells = cursor.execute("SELECT * FROM umts_cells WHERE id_name = ?", (site_query,)).fetchall()
    umts_act = sum(1 for c in umts_cells if "ACT" in (c["activity_status"] or "").upper())
    umts_inact = len(umts_cells) - umts_act
    
    lte_cells = cursor.execute("SELECT * FROM lte_cells WHERE id_name = ?", (site_query,)).fetchall()
    lte_act = sum(1 for c in lte_cells if "ACT" in (c["activation_status"] or "").upper())
    lte_inact = len(lte_cells) - lte_act
    
    nr_cells = cursor.execute("SELECT * FROM nr_cells WHERE id_name = ?", (site_query,)).fetchall()
    nr_act = sum(1 for c in nr_cells if "ACT" in (c["activation_status"] or "").upper())
    nr_inact = len(nr_cells) - nr_act
    
    rru_list = cursor.execute("SELECT * FROM rru_items WHERE id_name = ?", (site_query,)).fetchall()
    conn.close()
    
    return render_template(
        "pipeline.html",
        site_id=site_query,
        site_counts={
            "gsm": {"act": gsm_act, "inact": gsm_inact},
            "umts": {"act": umts_act, "inact": umts_inact},
            "lte": {"act": lte_act, "inact": lte_inact},
            "nr": {"act": nr_act, "inact": nr_inact}
        },
        site_rru=[dict(r) for r in rru_list]
    )

@app.route("/cells")
def cells():
    tech = request.args.get("tech", "lte").lower()
    search = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    page = int(request.args.get("page", 1))
    per_page = 50
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    table_map = {
        "gsm": "gsm_cells",
        "umts": "umts_cells",
        "lte": "lte_cells",
        "nr": "nr_cells"
    }
    table = table_map.get(tech, "lte_cells")

    conditions = []
    params = []

    if search:
        conditions.append("(id_name LIKE ? OR cell_name LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])

    if status:
        if tech in ["gsm", "umts"]:
            conditions.append("activity_status LIKE ?")
        else:
            conditions.append("activation_status LIKE ?")
        params.append(f"%{status}%")

    where_str = "WHERE " + " AND ".join(conditions) if conditions else ""

    # Count
    total_count = cursor.execute(f"SELECT COUNT(*) FROM {table} {where_str}", params).fetchone()[0]

    # Records
    records = cursor.execute(f"""
        SELECT * FROM {table} {where_str} LIMIT ? OFFSET ?
    """, params + [per_page, offset]).fetchall()

    conn.close()
    total_pages = (total_count + per_page - 1) // per_page

    return render_template(
        "cells.html",
        tech=tech,
        search=search,
        status=status,
        records=[dict(r) for r in records],
        page=page,
        total_pages=total_pages,
        total_count=total_count
    )

@app.route("/inventory")
def inventory():
    search = request.args.get("q", "").strip()
    inv_type = request.args.get("type", "boards") # 'boards' or 'rru'
    page = int(request.args.get("page", 1))
    per_page = 50
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    if inv_type == "rru":
        conditions = []
        params = []
        if search:
            conditions.append("(id_name LIKE ? OR modelo_rru LIKE ? OR no_serie LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        where_str = "WHERE " + " AND ".join(conditions) if conditions else ""
        total_count = cursor.execute(f"SELECT COUNT(*) FROM rru_items {where_str}", params).fetchone()[0]
        records = cursor.execute(f"""
            SELECT * FROM rru_items {where_str} LIMIT ? OFFSET ?
        """, params + [per_page, offset]).fetchall()
    else:
        conditions = []
        params = []
        if search:
            conditions.append("(id_name LIKE ? OR sn_barcode LIKE ? OR board_name LIKE ? OR model LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])
        where_str = "WHERE " + " AND ".join(conditions) if conditions else ""
        total_count = cursor.execute(f"SELECT COUNT(*) FROM inventory_boards {where_str}", params).fetchone()[0]
        records = cursor.execute(f"""
            SELECT * FROM inventory_boards {where_str} LIMIT ? OFFSET ?
        """, params + [per_page, offset]).fetchall()

    conn.close()
    total_pages = (total_count + per_page - 1) // per_page

    return render_template(
        "inventory.html",
        inv_type=inv_type,
        search=search,
        records=[dict(r) for r in records],
        page=page,
        total_pages=total_pages,
        total_count=total_count
    )

@app.route("/import-export")
def import_export():
    conn = get_db_connection()
    cursor = conn.cursor()
    logs = cursor.execute("SELECT * FROM import_metadata ORDER BY id DESC LIMIT 10").fetchall()
    conn.close()
    return render_template(
        "import_export.html",
        excel_path=EXCEL_SOURCE_PATH,
        excel_exists=os.path.exists(EXCEL_SOURCE_PATH),
        excel_size_mb=round(os.path.getsize(EXCEL_SOURCE_PATH)/(1024*1024), 1) if os.path.exists(EXCEL_SOURCE_PATH) else 0,
        etl_state=etl_state,
        logs=[dict(l) for l in logs]
    )

# API: Autocomplete Sites
@app.route("/api/autocomplete/sites")
def autocomplete_sites():
    term = request.args.get("term", "").strip().upper()
    if not term or len(term) < 2:
        return jsonify([])
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute("""
        SELECT DISTINCT id_name FROM lte_cells WHERE id_name LIKE ? LIMIT 15
    """, (f"{term}%",)).fetchall()
    conn.close()
    return jsonify([r[0] for r in rows if r[0]])

# API: Export Site or Filter to Excel
@app.route("/api/export/site/<site_id>")
def download_site_excel(site_id):
    try:
        clean_id = site_id.strip().upper() if site_id != "all" else None
        filepath = export_site_excel(clean_id)
        filename = os.path.basename(filepath)
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API: Trigger ETL in Background
def run_etl_worker(excel_path):
    global etl_state
    etl_state["running"] = True
    etl_state["error"] = None
    etl_state["progress"] = "Iniciando lectura y carga de Excel..."
    try:
        summary = run_full_etl(excel_path)
        etl_state["summary"] = summary
        etl_state["progress"] = "Importación completada con éxito."
    except Exception as e:
        etl_state["error"] = str(e)
        etl_state["progress"] = f"Error durante la importación: {str(e)}"
    finally:
        etl_state["running"] = False

@app.route("/api/etl/start", methods=["POST"])
def start_etl():
    global etl_state
    if etl_state["running"]:
        return jsonify({"status": "already_running"})
    custom_path = request.form.get("excel_path") or EXCEL_SOURCE_PATH
    t = threading.Thread(target=run_etl_worker, args=(custom_path,))
    t.daemon = True
    t.start()
    return jsonify({"status": "started"})

@app.route("/api/etl/status")
def check_etl_status():
    global etl_state
    return jsonify(etl_state)

if __name__ == "__main__":
    init_db()
    print(f"Starting Telcel As-Built Web Server on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
