"""
reporte_pdf.py
Genera un reporte PDF del dashboard de Órdenes de Compra.
Uso: llamar a generar_reporte_pdf(...) y recibir bytes del PDF.
"""
import io
from collections import defaultdict
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)

# ── Paleta de colores ─────────────────────────────────────────────
C_NAVY      = colors.HexColor("#1e3a5f")
C_BLUE      = colors.HexColor("#2d5a8e")
C_ACCENT    = colors.HexColor("#3b82f6")
C_GREEN     = colors.HexColor("#10b981")
C_AMBER     = colors.HexColor("#f59e0b")
C_RED       = colors.HexColor("#ef4444")
C_SLATE     = colors.HexColor("#475569")
C_LIGHTGRAY = colors.HexColor("#f1f5f9")
C_BORDERGRAY= colors.HexColor("#cbd5e1")
C_WHITE     = colors.white
C_DARKTEXT  = colors.HexColor("#1e293b")

# Ancho util A4 con margenes de 1.5 cm a cada lado
PAGE_W = 18 * cm


def _styles():
    base = getSampleStyleSheet()
    custom = {
        "ReportTitle": ParagraphStyle(
            "ReportTitle", parent=base["Title"],
            fontSize=20, textColor=C_WHITE, alignment=TA_LEFT,
            fontName="Helvetica-Bold", leading=26,
        ),
        "ReportSub": ParagraphStyle(
            "ReportSub", parent=base["Normal"],
            fontSize=9, textColor=colors.HexColor("#93c5fd"),
            alignment=TA_LEFT, fontName="Helvetica",
        ),
        "SectionTitle": ParagraphStyle(
            "SectionTitle", parent=base["Heading2"],
            fontSize=10, textColor=C_NAVY, fontName="Helvetica-Bold",
            spaceBefore=12, spaceAfter=5,
        ),
        "KPILabel": ParagraphStyle(
            "KPILabel", fontSize=7, textColor=C_SLATE,
            fontName="Helvetica", alignment=TA_CENTER,
        ),
        "TableCell": ParagraphStyle(
            "TableCell", fontSize=8, textColor=C_DARKTEXT,
            fontName="Helvetica", alignment=TA_LEFT,
        ),
        "Footer": ParagraphStyle(
            "Footer", fontSize=7, textColor=C_SLATE,
            fontName="Helvetica", alignment=TA_CENTER,
        ),
        "AlertRed": ParagraphStyle(
            "AlertRed", fontSize=8, textColor=C_RED,
            fontName="Helvetica-Bold", alignment=TA_LEFT,
        ),
        "AlertAmber": ParagraphStyle(
            "AlertAmber", fontSize=8, textColor=colors.HexColor("#92400e"),
            fontName="Helvetica-Bold", alignment=TA_LEFT,
        ),
    }
    return {**{k: base[k] for k in base.byName}, **custom}


# ── Helpers ───────────────────────────────────────────────────────

def _header_table(styles, fecha_reporte):
    title_p = Paragraph("Reporte de Ordenes de Compra", styles["ReportTitle"])
    sub_p   = Paragraph(
        f"Dashboard Analitico  .  Generado el {fecha_reporte}",
        styles["ReportSub"]
    )
    inner = Table([[title_p], [sub_p]], colWidths=[PAGE_W])
    inner.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), C_NAVY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING",   (0, 0), (-1, 0),  14),
        ("BOTTOMPADDING",(0, 0), (-1, 0),  2),
        ("TOPPADDING",   (0, 1), (-1, 1),  2),
        ("BOTTOMPADDING",(0, 1), (-1, 1),  12),
    ]))
    return inner


def _kpi_table(styles, kpis):
    n = len(kpis)
    col_w = [PAGE_W / n] * n
    headers = [Paragraph(k[0], styles["KPILabel"]) for k in kpis]
    values  = []
    for _, v, c in kpis:
        vs = ParagraphStyle(
            "_kv", fontSize=16, textColor=colors.HexColor(c),
            fontName="Helvetica-Bold", alignment=TA_CENTER,
        )
        values.append(Paragraph(str(v), vs))
    t = Table([headers, values], colWidths=col_w, rowHeights=[18, 30])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  C_LIGHTGRAY),
        ("BACKGROUND",   (0, 1), (-1, 1),  C_WHITE),
        ("BOX",          (0, 0), (-1, -1), 0.75, C_BORDERGRAY),
        ("INNERGRID",    (0, 0), (-1, -1), 0.5,  C_BORDERGRAY),
        ("TOPPADDING",   (0, 0), (-1, 0),  6),
        ("BOTTOMPADDING",(0, 0), (-1, 0),  4),
        ("TOPPADDING",   (0, 1), (-1, 1),  4),
        ("BOTTOMPADDING",(0, 1), (-1, 1),  8),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def _section(styles, title, icon=""):
    return KeepTogether([
        HRFlowable(width="100%", thickness=1, color=C_BORDERGRAY, spaceAfter=4),
        Paragraph(f"{icon}  {title}" if icon else title, styles["SectionTitle"]),
    ])


def _std_table_style(header_color=None):
    hc = header_color or C_NAVY
    return TableStyle([
        # Cabecera
        ("BACKGROUND",    (0, 0), (-1, 0),  hc),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  C_WHITE),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  8),
        ("ALIGN",         (0, 0), (-1, 0),  "CENTER"),
        ("VALIGN",        (0, 0), (-1, 0),  "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, 0),  7),
        ("BOTTOMPADDING", (0, 0), (-1, 0),  7),
        ("LEFTPADDING",   (0, 0), (-1, 0),  8),
        ("RIGHTPADDING",  (0, 0), (-1, 0),  8),
        ("LINEBELOW",     (0, 0), (-1, 0),  1.0, hc),
        # Filas de datos
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [C_WHITE, C_LIGHTGRAY]),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 8),
        ("TEXTCOLOR",     (0, 1), (-1, -1), C_DARKTEXT),
        ("VALIGN",        (0, 1), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("LEFTPADDING",   (0, 1), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 1), (-1, -1), 8),
        # Bordes
        ("BOX",           (0, 0), (-1, -1), 0.75, C_BORDERGRAY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3,  C_BORDERGRAY),
    ])


# ── Función principal ─────────────────────────────────────────────

def generar_reporte_pdf(ordenes_dash, detalles_dash, movs_dash, stock_data_dash):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.8 * cm,
        title="Reporte Ordenes de Compra",
        author="Sistema de Gestion de Compras",
    )

    styles = _styles()
    story  = []
    fecha_reporte = datetime.now().strftime("%d/%m/%Y %H:%M")

    # ── 1. ENCABEZADO
    story.append(_header_table(styles, fecha_reporte))
    story.append(Spacer(1, 0.4 * cm))

    # ── 2. KPIs
    total_oc   = len(ordenes_dash)
    pendientes = sum(1 for o in ordenes_dash if o["estado"] == "PENDIENTE")
    aprobadas  = sum(1 for o in ordenes_dash if o["estado"] == "APROBADA")
    anuladas   = sum(1 for o in ordenes_dash if o["estado"] == "ANULADA")

    monto_por_orden = defaultdict(float)
    for d in detalles_dash:
        sub = float(d.get("subtotal") or (d["cantidad"] * d["precio_unitario"]))
        monto_por_orden[d["id_orden"]] += sub

    monto_aprobado = sum(
        monto_por_orden[o["id"]] for o in ordenes_dash if o["estado"] == "APROBADA"
    )
    sin_stock  = [s for s in stock_data_dash if int(s["stock_actual"]) <= 0]
    stock_bajo = [s for s in stock_data_dash
                  if 0 < int(s["stock_actual"]) <= int(s.get("stock_minimo") or 0)]

    kpis = [
        ("Total OC",       str(total_oc),               "#1e3a5f"),
        ("Pendientes",     str(pendientes),              "#f59e0b"),
        ("Aprobadas",      str(aprobadas),               "#10b981"),
        ("Anuladas",       str(anuladas),                "#ef4444"),
        ("Monto Aprobado", f"S/ {monto_aprobado:,.0f}", "#2d5a8e"),
        ("Sin Stock",      str(len(sin_stock)),          "#dc2626"),
    ]
    story.append(_section(styles, "Indicadores Generales"))
    story.append(_kpi_table(styles, kpis))
    story.append(Spacer(1, 0.3 * cm))

    # ── 3. ORDENES POR ESTADO  (5 + 3 + 5.5 + 4.5 = 18 cm)
    story.append(_section(styles, "Resumen por Estado de Orden"))
    estado_monto = defaultdict(float)
    for o in ordenes_dash:
        estado_monto[o["estado"]] += monto_por_orden.get(o["id"], 0)

    data_estado = [["Estado", "Cantidad", "Monto (S/)", "% del Total"]]
    total_m = sum(estado_monto.values()) or 1
    for est in ["PENDIENTE", "APROBADA", "ANULADA"]:
        cnt = sum(1 for o in ordenes_dash if o["estado"] == est)
        mon = estado_monto[est]
        pct = mon / total_m * 100
        data_estado.append([est, str(cnt), f"S/ {mon:,.2f}", f"{pct:.1f}%"])

    t_estado = Table(data_estado, colWidths=[5*cm, 3*cm, 5.5*cm, 4.5*cm])
    ts = _std_table_style()
    ts.add("ALIGN", (1, 1), (-1, -1), "RIGHT")
    estado_colors = {"PENDIENTE": colors.HexColor("#fffbeb"),
                     "APROBADA":  colors.HexColor("#f0fdf4"),
                     "ANULADA":   colors.HexColor("#fef2f2")}
    for i, row in enumerate(data_estado[1:], 1):
        ts.add("BACKGROUND", (0, i), (-1, i), estado_colors.get(row[0], C_WHITE))
    t_estado.setStyle(ts)
    story.append(t_estado)
    story.append(Spacer(1, 0.3 * cm))

    # ── 4. ORDENES POR MES  (4 + 3.5 + 5.25 + 5.25 = 18 cm)
    story.append(_section(styles, "Ordenes de Compra por Mes"))
    mes_count = defaultdict(int)
    mes_monto = defaultdict(float)
    for o in ordenes_dash:
        mes = o["fecha"][:7]
        mes_count[mes] += 1
        mes_monto[mes] += monto_por_orden.get(o["id"], 0)

    if mes_count:
        data_mes = [["Mes", "Cantidad OC", "Monto Total (S/)", "Monto c/IGV (S/)"]]
        for mes in sorted(mes_count.keys()):
            mon = mes_monto[mes]
            data_mes.append([mes, str(mes_count[mes]),
                             f"S/ {mon:,.2f}", f"S/ {mon*1.18:,.2f}"])
        t_mes = Table(data_mes, colWidths=[4*cm, 3.5*cm, 5.25*cm, 5.25*cm])
        ts_mes = _std_table_style(C_BLUE)
        ts_mes.add("ALIGN", (1, 1), (-1, -1), "RIGHT")
        t_mes.setStyle(ts_mes)
        story.append(t_mes)
    story.append(Spacer(1, 0.3 * cm))

    # ── 5. ANALISIS ABC  (1 + 9 + 3.5 + 2.5 + 2 = 18 cm)
    story.append(_section(styles, "Analisis ABC de Productos (por monto comprado)"))
    monto_prod  = defaultdict(float)
    nombre_prod = {}
    for d in detalles_dash:
        prod = d.get("producto") or {}
        pid  = prod.get("id") or "?"
        sub  = float(d.get("subtotal") or (d["cantidad"] * d["precio_unitario"]))
        monto_prod[pid]  += sub
        nombre_prod[pid]  = prod.get("nombre", "-")

    if monto_prod:
        sorted_prods = sorted(monto_prod.items(), key=lambda x: x[1], reverse=True)
        total_abc = sum(v for _, v in sorted_prods) or 1
        acum = 0
        abc_rows = []
        for pid, monto in sorted_prods:
            acum += monto
            pct_acum = acum / total_abc * 100
            clase = "A" if pct_acum <= 80 else ("B" if pct_acum <= 95 else "C")
            abc_rows.append((nombre_prod[pid], monto, pct_acum, clase))

        data_abc = [["#", "Producto", "Monto (S/)", "% Acum.", "Clase"]]
        for i, (nom, mon, pct, cls) in enumerate(abc_rows, 1):
            data_abc.append([str(i), nom[:45], f"S/ {mon:,.2f}", f"{pct:.1f}%", cls])

        col_w_abc = [1*cm, 9*cm, 3.5*cm, 2.5*cm, 2*cm]
        t_abc = Table(data_abc, colWidths=col_w_abc, repeatRows=1)
        ts_abc = _std_table_style(colors.HexColor("#065f46"))
        ts_abc.add("ALIGN", (2, 1), (-1, -1), "RIGHT")
        ts_abc.add("ALIGN", (4, 1), (4, -1), "CENTER")

        abc_color = {"A": colors.HexColor("#dbeafe"),
                     "B": colors.HexColor("#fef3c7"),
                     "C": colors.HexColor("#f1f5f9")}
        for i, row in enumerate(data_abc[1:], 1):
            ts_abc.add("BACKGROUND", (0, i), (-1, i), abc_color.get(row[4], C_WHITE))
            fc = {"A": C_ACCENT, "B": C_AMBER, "C": C_SLATE}.get(row[4], C_SLATE)
            ts_abc.add("TEXTCOLOR", (4, i), (4, i), fc)
            ts_abc.add("FONTNAME",  (4, i), (4, i), "Helvetica-Bold")
        t_abc.setStyle(ts_abc)
        story.append(t_abc)

        # Resumen ABC  (2 + 2.5 + 5 + 8.5 = 18 cm)
        story.append(Spacer(1, 0.2 * cm))
        resumen_abc = defaultdict(lambda: {"count": 0, "monto": 0.0})
        for _, mon, _, cls in abc_rows:
            resumen_abc[cls]["count"] += 1
            resumen_abc[cls]["monto"] += mon

        sum_data = [["Clase", "Productos", "Monto Total (S/)", "Descripcion"]]
        for cls, desc in [("A","Alto valor - 80% del gasto"),
                           ("B","Valor medio - hasta 95%"),
                           ("C","Bajo valor - restante 5%")]:
            sum_data.append([cls, str(resumen_abc[cls]["count"]),
                             f"S/ {resumen_abc[cls]['monto']:,.2f}", desc])
        t_sum_abc = Table(sum_data, colWidths=[2*cm, 2.5*cm, 5*cm, 8.5*cm])
        ts2 = _std_table_style(colors.HexColor("#1e3a5f"))
        ts2.add("ALIGN", (2, 1), (2, -1), "RIGHT")
        for i, cls in enumerate(["A","B","C"], 1):
            ts2.add("BACKGROUND", (0, i), (-1, i), abc_color.get(cls, C_WHITE))
        t_sum_abc.setStyle(ts2)
        story.append(t_sum_abc)

    story.append(Spacer(1, 0.3 * cm))

    # ── 6. TOP PROVEEDORES  (1 + 7.5 + 2 + 3.75 + 3.75 = 18 cm)
    story.append(_section(styles, "Top Proveedores por Monto"))
    prov_monto = defaultdict(float)
    prov_count = defaultdict(int)
    for o in ordenes_dash:
        nombre_pv = (o.get("proveedor") or {}).get("nombre", "Sin nombre")
        prov_monto[nombre_pv] += monto_por_orden.get(o["id"], 0)
        prov_count[nombre_pv] += 1

    if prov_monto:
        top_provs = sorted(prov_monto.items(), key=lambda x: x[1], reverse=True)[:10]
        data_prov = [["#", "Proveedor", "N OC", "Monto Total (S/)", "Monto c/IGV (S/)"]]
        for i, (nom, mon) in enumerate(top_provs, 1):
            data_prov.append([str(i), nom[:40], str(prov_count[nom]),
                              f"S/ {mon:,.2f}", f"S/ {mon*1.18:,.2f}"])
        t_prov = Table(data_prov, colWidths=[1*cm, 7.5*cm, 2*cm, 3.75*cm, 3.75*cm])
        ts_prov = _std_table_style(colors.HexColor("#5b21b6"))
        ts_prov.add("ALIGN", (2, 1), (-1, -1), "RIGHT")
        t_prov.setStyle(ts_prov)
        story.append(t_prov)
    story.append(Spacer(1, 0.3 * cm))

    # ── 7. PRODUCTOS MAS COMPRADOS  (1 + 9 + 2.5 + 2.5 + 3 = 18 cm)
    story.append(_section(styles, "Cantidad de Veces Comprado por Producto"))
    prod_oc = defaultdict(lambda: {"nombre": "", "veces": 0, "cantidad": 0, "monto": 0.0})
    for d in detalles_dash:
        prod = d.get("producto") or {}
        pid  = prod.get("id") or "?"
        sub  = float(d.get("subtotal") or (d["cantidad"] * d["precio_unitario"]))
        prod_oc[pid]["nombre"]    = prod.get("nombre", "-")
        prod_oc[pid]["veces"]    += 1
        prod_oc[pid]["cantidad"] += int(d["cantidad"])
        prod_oc[pid]["monto"]    += sub

    if prod_oc:
        tabla_prod = sorted(prod_oc.values(), key=lambda x: x["veces"], reverse=True)
        data_prod = [["#", "Producto", "Veces en OC", "Unidades", "Monto (S/)"]]
        for i, row in enumerate(tabla_prod, 1):
            data_prod.append([str(i), row["nombre"][:45],
                              str(row["veces"]), str(row["cantidad"]),
                              f"S/ {row['monto']:,.2f}"])
        t_prod = Table(data_prod, colWidths=[1*cm, 9*cm, 2.5*cm, 2.5*cm, 3*cm])
        ts_prod = _std_table_style(colors.HexColor("#0f766e"))
        ts_prod.add("ALIGN", (2, 1), (-1, -1), "RIGHT")
        t_prod.setStyle(ts_prod)
        story.append(t_prod)
    story.append(Spacer(1, 0.3 * cm))

    # ── 8. MOVIMIENTOS POR TIPO  (4 + 5 + 4.5 + 4.5 = 18 cm)
    story.append(_section(styles, "Movimientos de Inventario por Tipo"))
    MOTIVO_LABEL_D = {
        "COMPRA": "Compra", "DEVOLUCION": "Devolucion",
        "VENTA": "Venta", "INHABILITADO": "Inhabilitado", "USO_INTERNO": "Uso Interno",
    }
    tipo_count = defaultdict(int)
    tipo_cant  = defaultdict(int)
    for m in movs_dash:
        tipo_count[m["tipo"]] += 1
        tipo_cant[m["tipo"]]  += int(m["cantidad"])

    if tipo_count:
        data_mov = [["Tipo", "Etiqueta", "N Movimientos", "Unidades Totales"]]
        for tipo in sorted(tipo_count.keys()):
            data_mov.append([tipo, MOTIVO_LABEL_D.get(tipo, tipo),
                            str(tipo_count[tipo]), str(tipo_cant[tipo])])
        t_mov = Table(data_mov, colWidths=[4*cm, 5*cm, 4.5*cm, 4.5*cm])
        ts_mov = _std_table_style(colors.HexColor("#1e40af"))
        ts_mov.add("ALIGN", (2, 1), (-1, -1), "RIGHT")
        t_mov.setStyle(ts_mov)
        story.append(t_mov)
    story.append(Spacer(1, 0.3 * cm))

    # ── 9. ALERTAS DE STOCK
    story.append(_section(styles, "Alertas de Stock"))

    if sin_stock:
        story.append(Paragraph(f"Productos SIN STOCK ({len(sin_stock)})", styles["AlertRed"]))
        story.append(Spacer(1, 0.1 * cm))
        # 2.5 + 9.5 + 2.5 + 3.5 = 18 cm
        data_ss = [["Codigo", "Producto", "Unidad", "Stock Minimo"]]
        for s in sin_stock:
            data_ss.append([s.get("codigo","—"), s["nombre"][:45],
                           s["unidad"], str(int(s.get("stock_minimo") or 0))])
        t_ss = Table(data_ss, colWidths=[2.5*cm, 9.5*cm, 2.5*cm, 3.5*cm])
        ts_ss = _std_table_style(C_RED)
        ts_ss.add("ALIGN", (3, 1), (3, -1), "RIGHT")
        for i in range(1, len(data_ss)):
            ts_ss.add("BACKGROUND", (0, i), (-1, i), colors.HexColor("#fef2f2"))
        t_ss.setStyle(ts_ss)
        story.append(t_ss)
        story.append(Spacer(1, 0.2 * cm))

    if stock_bajo:
        story.append(Paragraph(f"Productos con STOCK BAJO ({len(stock_bajo)})", styles["AlertAmber"]))
        story.append(Spacer(1, 0.1 * cm))
        # 2.5 + 8.5 + 2 + 2.5 + 2.5 = 18 cm
        data_sb = [["Codigo", "Producto", "Unidad", "Stock Actual", "Stock Minimo"]]
        for s in stock_bajo:
            data_sb.append([s.get("codigo","—"), s["nombre"][:40],
                           s["unidad"], str(int(s["stock_actual"])),
                           str(int(s.get("stock_minimo") or 0))])
        t_sb = Table(data_sb, colWidths=[2.5*cm, 8.5*cm, 2*cm, 2.5*cm, 2.5*cm])
        ts_sb = _std_table_style(C_AMBER)
        ts_sb.add("ALIGN", (3, 1), (-1, -1), "RIGHT")
        for i in range(1, len(data_sb)):
            ts_sb.add("BACKGROUND", (0, i), (-1, i), colors.HexColor("#fffbeb"))
        t_sb.setStyle(ts_sb)
        story.append(t_sb)

    if not sin_stock and not stock_bajo:
        story.append(Paragraph("Todo el inventario esta en niveles correctos.", styles["SectionTitle"]))

    story.append(Spacer(1, 0.4 * cm))

    # ── 10. STOCK POR CATEGORIA  (5 + 3 + 3.5 + 3.5 + 3 = 18 cm)
    story.append(_section(styles, "Stock Actual por Categoria"))
    cat_stock = defaultdict(lambda: {"ok": 0, "bajo": 0, "cero": 0, "total": 0})
    for s in stock_data_dash:
        cat = s.get("categoria") or "Sin categoria"
        act = int(s["stock_actual"])
        mni = int(s.get("stock_minimo") or 0)
        cat_stock[cat]["total"] += max(0, act)
        if act <= 0:
            cat_stock[cat]["cero"] += 1
        elif act <= mni:
            cat_stock[cat]["bajo"] += 1
        else:
            cat_stock[cat]["ok"]   += 1

    if cat_stock:
        data_cat = [["Categoria", "Stock Total", "Productos OK", "Stock Bajo", "Sin Stock"]]
        for cat, v in sorted(cat_stock.items()):
            data_cat.append([cat, str(v["total"]), str(v["ok"]),
                            str(v["bajo"]), str(v["cero"])])
        t_cat = Table(data_cat, colWidths=[5*cm, 3*cm, 3.5*cm, 3.5*cm, 3*cm])
        ts_cat = _std_table_style(C_NAVY)
        ts_cat.add("ALIGN", (1, 1), (-1, -1), "RIGHT")
        t_cat.setStyle(ts_cat)
        story.append(t_cat)

    # ── PIE DE PAGINA
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDERGRAY))
    story.append(Spacer(1, 0.1 * cm))
    story.append(Paragraph(
        f"Sistema de Gestion de Compras  .  Reporte generado el {fecha_reporte}",
        styles["Footer"]
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
