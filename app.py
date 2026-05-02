import streamlit as st
from supabase import create_client
from datetime import date, datetime

# ── Config ───────────────────────────────────────────────────
# Las claves se leen desde los "secrets" (archivo secreto local o configuración en Streamlit Cloud)
# Nunca escribas las claves directamente aquí si vas a subir el código a GitHub
SUPA_URL = st.secrets["SUPA_URL"]
SUPA_KEY = st.secrets["SUPA_KEY"]

st.set_page_config(page_title="Órdenes de Compra", layout="wide", page_icon="📦")

# ── CSS ─────────────────────────────────────────────────────
# Estilos visuales de toda la app: colores, fuentes, tarjetas, badges, etc.
# Se inyectan directamente como HTML para personalizar la apariencia de Streamlit
st.markdown("""
<style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
    section[data-testid="stMain"] > div { background-color: #f1f5f9 !important; }

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stNumberInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    }
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder { color: #94a3b8 !important; }

    .stDateInput input,
    .stDateInput [data-baseweb="input"] input {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }
    .stDateInput [data-baseweb="input"] div[role="button"] svg { fill: #64748b !important; }

    .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] div[class*="ValueContainer"],
    .stSelectbox [data-baseweb="select"] div[class*="singleValue"],
    .stSelectbox [data-baseweb="select"] div[class*="placeholder"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    .stSelectbox [data-baseweb="select"] > div {
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }
    [data-baseweb="popover"] ul,
    [data-baseweb="menu"],
    [data-baseweb="menu"] li,
    [role="listbox"],
    [role="option"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    [role="option"]:hover { background-color: #eff6ff !important; color: #1e40af !important; }
    .stSelectbox svg { color: #64748b !important; fill: #64748b !important; }

    .stTextInput label, .stSelectbox label, .stTextArea label,
    .stDateInput label, .stNumberInput label {
        font-size: 11px !important;
        font-weight: 700 !important;
        color: #475569 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.6px !important;
    }

    p, .stMarkdown p, .stMarkdown span, .stCaption,
    [data-testid="stMarkdownContainer"] p { color: #475569 !important; }

    [data-testid="metric-container"] label { color: #64748b !important; font-size: 12px !important; }
    [data-testid="metric-container"] [data-testid="metric-value"] { color: #1e293b !important; font-weight: 800 !important; }

    /* Disabled inputs */
    .stTextInput input:disabled,
    .stDateInput input:disabled,
    .stSelectbox [data-baseweb="select"][aria-disabled="true"] > div {
        background-color: #f8fafc !important;
        color: #1e293b !important;
        border-color: #e2e8f0 !important;
        -webkit-text-fill-color: #1e293b !important;
        opacity: 1 !important;
    }

    .stApp { background-color: #f1f5f9 !important; }

    .oc-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a8e 100%);
        color: white !important;
        padding: 16px 24px;
        border-radius: 12px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 4px 12px rgba(30,58,95,0.25);
    }
    .oc-header h2, .oc-header h2 * { margin: 0; font-size: 20px; font-weight: 800; color: white !important; -webkit-text-fill-color: white !important; }
    .oc-header span.sub { font-size: 12px; opacity: 0.8; color: white !important; }

    .card {
        background: white;
        border-radius: 12px;
        padding: 18px 22px 22px;
        border: 1px solid #e2e8f0;
        margin-bottom: 16px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .card-title {
        font-size: 11px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #64748b !important;
        margin-bottom: 16px;
        padding-bottom: 10px;
        border-bottom: 2px solid #e2e8f0;
    }
    .card-title.blue   { border-color: #3b82f6 !important; color: #1e40af !important; }
    .card-title.orange { border-color: #f59e0b !important; color: #92400e !important; }
    .card-title.green  { border-color: #10b981 !important; color: #065f46 !important; }
    .card-title.purple { border-color: #8b5cf6 !important; color: #5b21b6 !important; }
    .card-title.red    { border-color: #ef4444 !important; color: #991b1b !important; }
    .card-title.teal   { border-color: #14b8a6 !important; color: #0f766e !important; }

    .badge-entrada { background:#d1fae5; color:#065f46 !important; border:1.5px solid #6ee7b7; }
    .badge-salida  { background:#fee2e2; color:#991b1b !important; border:1.5px solid #fca5a5; }
    .mov-entrada   { color:#059669 !important; font-weight:800; font-size:15px; }
    .mov-salida    { color:#dc2626 !important; font-weight:800; font-size:15px; }

    .stock-ok      { color:#059669 !important; font-weight:800; }
    .stock-bajo    { color:#dc2626 !important; font-weight:800; }
    .stock-cero    { color:#6b7280 !important; font-weight:800; }
    .alerta-bajo   { background:#fef2f2; border:1.5px solid #fca5a5; border-radius:8px;
                     padding:3px 10px; color:#991b1b !important; font-size:11px; font-weight:700; }

    .kd-entrada  { background:#f0fdf4; }
    .kd-salida   { background:#fff7f7; }
    .kd-saldo-ok { color:#059669 !important; font-weight:900; }
    .kd-saldo-bajo { color:#dc2626 !important; font-weight:900; }

    .badge {
        display: inline-block;
        padding: 5px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 0.6px;
    }
    .badge-pendiente { background: #fef3c7; color: #92400e !important; border: 1.5px solid #fcd34d; }
    .badge-aprobada  { background: #d1fae5; color: #065f46 !important; border: 1.5px solid #6ee7b7; }
    .badge-anulada   { background: #fee2e2; color: #991b1b !important; border: 1.5px solid #fca5a5; }

    .numero-oc-val {
        font-size: 24px !important;
        font-weight: 900 !important;
        color: #1e3a5f !important;
        letter-spacing: 1.5px;
        font-family: 'Courier New', monospace;
    }

    .total-box {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a8e 100%);
        border-radius: 10px;
        padding: 16px 20px;
        text-align: right;
        margin-top: 12px;
        box-shadow: 0 4px 12px rgba(30,58,95,0.3);
    }
    .total-box .lbl { font-size: 11px; color: rgba(255,255,255,0.75) !important; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; }
    .total-box .val { font-size: 30px; font-weight: 900; color: white !important; margin-top: 2px; }

    .th-row { display: flex; gap: 8px; padding: 6px 4px; background: #f8fafc; border-radius: 6px; margin-bottom: 4px; }
    .th-cell { font-size: 10px !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.7px; color: #64748b !important; }

    .item-row { padding: 8px 4px; border-bottom: 1px solid #f1f5f9; }
    .item-num   { color: #94a3b8 !important; font-size: 13px; }
    .item-code  { font-family: monospace; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 12px; color: #475569 !important; }
    .item-sub   { font-weight: 800 !important; color: #1e3a5f !important; }

    .empty-msg { color: #94a3b8 !important; font-style: italic; text-align: center; padding: 28px 0; font-size: 14px; }

    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.2rem !important; }

    .stTextInput label, .stSelectbox label, .stTextArea label,
    .stDateInput label, .stNumberInput label {
        font-size: 12px !important; font-weight: 700 !important;
        color: #475569 !important; text-transform: uppercase; letter-spacing: 0.5px;
    }

    hr { border-color: #e2e8f0 !important; margin: 6px 0 10px !important; }
</style>
""", unsafe_allow_html=True)

# ── Conexión a Supabase ───────────────────────────────────────
# @st.cache_resource guarda la conexión en memoria para no reconectarse
# cada vez que el usuario interactúa con la app (más rápido y eficiente)
@st.cache_resource
def get_client():
    return create_client(SUPA_URL, SUPA_KEY)

sb = get_client()

# ── Funciones de carga de datos ───────────────────────────────
# @st.cache_data(ttl=60) guarda el resultado por 60 segundos
# Así no se hace una consulta a la base de datos en cada clic del usuario

def cargar_proveedores():
    # Trae todos los proveedores ordenados por nombre
    res = sb.table("proveedor").select("id,nombre,ruc,telefono").order("nombre").execute()
    return res.data or []

@st.cache_data(ttl=60)
def cargar_productos():
    # Trae productos junto con el nombre de su categoría (join con tabla categoria)
    res = sb.table("producto").select(
        "id,codigo,nombre,unidad,precio_unitario,categoria:id_categoria(nombre)"
    ).order("codigo").execute()
    return res.data or []

@st.cache_data(ttl=30)
def cargar_numeros_ordenes():
    # Solo trae los números de OC para llenar el selector del filtro
    res = sb.table("orden_compra").select("numero").order("fecha", desc=True).execute()
    return [r["numero"] for r in (res.data or [])]

@st.cache_data(ttl=20)
def cargar_stock_actual():
    # Calcula el stock de cada producto sumando entradas y restando salidas
    # desde la tabla de movimientos (no usa una vista de base de datos)
    res_movs = sb.table("movimiento").select(
        "tipo,cantidad,id_producto,"
        "producto:id_producto(id,codigo,nombre,unidad,stock_minimo,categoria:id_categoria(nombre))"
    ).execute()
    movs = res_movs.data or []

    # Tipos que suman al stock
    ENTRADAS = {"COMPRA", "DEVOLUCION"}
    # Tipos que restan al stock
    SALIDAS  = {"VENTA", "INHABILITADO", "USO_INTERNO"}

    prods = {}
    for m in movs:
        prod = m.get("producto") or {}
        pid  = prod.get("id") or m.get("id_producto")
        if not pid:
            continue
        if pid not in prods:
            prods[pid] = {
                "id_producto":    pid,
                "codigo":         prod.get("codigo","—"),
                "nombre":         prod.get("nombre","—"),
                "unidad":         prod.get("unidad","—"),
                "categoria":      (prod.get("categoria") or {}).get("nombre","Sin categoría"),
                "stock_minimo":   prod.get("stock_minimo") or 0,
                "total_entradas": 0,
                "total_salidas":  0,
            }
        if m["tipo"] in ENTRADAS:
            prods[pid]["total_entradas"] += m["cantidad"]
        elif m["tipo"] in SALIDAS:
            prods[pid]["total_salidas"]  += m["cantidad"]

    result = []
    for pid, p in prods.items():
        # Stock actual = total entradas - total salidas
        p["stock_actual"] = p["total_entradas"] - p["total_salidas"]
        result.append(p)

    return sorted(result, key=lambda x: x["nombre"])

@st.cache_data(ttl=20)
def cargar_kardex(id_producto):
    # Construye el kardex de un producto: lista de movimientos con saldo acumulado
    # El saldo se va sumando o restando según el tipo de movimiento
    res = sb.table("movimiento").select(
        "id,fecha,tipo,cantidad,persona_contacto,observacion,created_at,"
        "orden:id_orden(numero)"
    ).eq("id_producto", id_producto).order("fecha").order("created_at").execute()
    movs = res.data or []

    ENTRADAS = {"COMPRA", "DEVOLUCION"}
    SALIDAS  = {"VENTA", "INHABILITADO", "USO_INTERNO"}

    saldo = 0
    rows  = []
    for i, m in enumerate(movs, 1):
        es_e    = m["tipo"] in ENTRADAS
        entrada = m["cantidad"] if es_e else 0
        salida  = m["cantidad"] if not es_e else 0
        saldo  += entrada - salida  # saldo acumulado hasta este movimiento
        orden   = (m.get("orden") or {}).get("numero") or "—"
        rows.append({
            "nro":              i,
            "fecha":            m["fecha"],
            "tipo":             m["tipo"],
            "entrada":          entrada,
            "salida":           salida,
            "saldo":            saldo,
            "persona_contacto": m.get("persona_contacto","—"),
            "orden_compra":     orden,
            "observacion":      m.get("observacion","—"),
        })
    return rows

# ── Número de OC automático ───────────────────────────────────
# Genera un número único para cada orden usando el año actual
# más los últimos 5 dígitos del timestamp (tiempo exacto en segundos)
# Ejemplo: OC-2025-48291
def gen_numero():
    ts = str(int(datetime.now().timestamp()))[-5:]
    return f"OC-{date.today().year}-{ts}"

# ── Estado de sesión ──────────────────────────────────────────
# st.session_state guarda variables mientras el usuario está en la app
# Sin esto, cada clic reinicia todas las variables a cero
defaults = {
    "detalle":          [],          # lista de productos agregados a la OC
    "oc_id":            None,        # ID de la OC guardada en base de datos
    "oc_numero":        gen_numero(), # número generado automáticamente
    "estado":           "PENDIENTE",
    "guardada":         False,       # controla si ya se guardó (bloquea edición)
    "mostrar_catalogo": False,
    "busqueda_cat":     "",
    "prov_index":       0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Encabezado principal ──────────────────────────────────────
# El badge de estado cambia de color según si la OC es Pendiente, Aprobada o Anulada
badge_class = {
    "PENDIENTE": "badge-pendiente",
    "APROBADA":  "badge-aprobada",
    "ANULADA":   "badge-anulada"
}.get(st.session_state.estado, "badge-pendiente")

st.markdown(f"""
<div class="oc-header">
    <div style="font-size:30px;">📦</div>
    <div>
        <h2>Orden de Compra</h2>
        <span class="sub">Sistema de gestión de compras</span>
    </div>
    <div style="margin-left:auto;">
        <span class="badge {badge_class}">{st.session_state.estado}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Pestañas de la app ────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📝  Nueva / Editar Orden",
    "🔍  Consultar Órdenes",
    "🔄  Movimientos",
    "📊  Kardex & Stock",
])

# ═══════════════════════════════════════════════════════════════
# TAB 1 — NUEVA / EDITAR ORDEN DE COMPRA
# ═══════════════════════════════════════════════════════════════
with tab1:

    # ── Botones de acción ─────────────────────────────────────
    # Los botones se deshabilitan automáticamente según el estado de la OC:
    # - "Guardar" solo si no está guardada aún
    # - "Aprobar" solo si está guardada y en estado PENDIENTE
    # - "Anular"  solo si está guardada y no está ya anulada
    bc1, bc2, bc3, bc4, _ = st.columns([1.3, 1, 1, 1.1, 2.6])

    with bc1:
        guardar_click = st.button(
            "💾 Guardar OC", type="primary", use_container_width=True,
            disabled=st.session_state.guardada
        )
    with bc2:
        aprobar_click = st.button(
            "✅ Aprobar", use_container_width=True,
            disabled=not st.session_state.guardada or st.session_state.estado != "PENDIENTE"
        )
    with bc3:
        anular_click = st.button(
            "❌ Anular", use_container_width=True,
            disabled=not st.session_state.guardada or st.session_state.estado == "ANULADA"
        )
    with bc4:
        nueva_click = st.button("➕ Nueva OC", use_container_width=True)

    # Al crear una nueva OC se limpian todos los datos de la sesión
    if nueva_click:
        st.session_state.detalle          = []
        st.session_state.oc_id            = None
        st.session_state.oc_numero        = gen_numero()
        st.session_state.estado           = "PENDIENTE"
        st.session_state.guardada         = False
        st.session_state.mostrar_catalogo = False
        st.session_state.busqueda_cat     = ""
        st.session_state.prov_index       = 0
        st.rerun()

    st.markdown("<div style='margin-bottom:14px;'></div>", unsafe_allow_html=True)

    # ── Cabecera de la orden ──────────────────────────────────
    st.markdown('<div class="card"><div class="card-title blue">📋 Cabecera — Orden de Compra</div>', unsafe_allow_html=True)

    proveedores = cargar_proveedores()
    opciones_prov = ["— Seleccionar proveedor —"] + [f"{p['ruc']} — {p['nombre']}" for p in proveedores]
    # Diccionario para acceder al proveedor completo desde su etiqueta visual
    prov_map = {f"{p['ruc']} — {p['nombre']}": p for p in proveedores}

    col_n, col_f, col_p, col_t = st.columns([1.2, 1, 2.2, 1])

    with col_n:
        st.markdown(
            "<div style='font-size:11px;font-weight:700;text-transform:uppercase;color:#475569;margin-bottom:6px;letter-spacing:0.5px;'>Número OC</div>"
            f"<div class='numero-oc-val'>{st.session_state.oc_numero}</div>",
            unsafe_allow_html=True
        )

    with col_f:
        fecha_oc = st.date_input("Fecha", value=date.today(), disabled=st.session_state.guardada)

    with col_p:
        prov_label = st.selectbox(
            "Proveedor",
            options=opciones_prov,
            index=st.session_state.prov_index,
            disabled=st.session_state.guardada,
            key="sel_proveedor"
        )
        prov_sel = prov_map.get(prov_label)
        if prov_label in opciones_prov:
            st.session_state.prov_index = opciones_prov.index(prov_label)

    with col_t:
        # Teléfono se llena automáticamente según el proveedor seleccionado
        st.text_input(
            "Teléfono",
            value=prov_sel["telefono"] if prov_sel else "",
            disabled=True,
            placeholder="Auto"
        )

    observacion = st.text_area(
        "Observación (opcional)",
        placeholder="Notas adicionales para esta orden...",
        height=72,
        disabled=st.session_state.guardada,
        key="observacion"
    )

    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
    col_btn, _ = st.columns([2.5, 5])
    with col_btn:
        if not st.session_state.guardada:
            label_cat = "🔽 Ocultar catálogo de productos" if st.session_state.mostrar_catalogo else "🔍 Agregar productos del catálogo"
            if st.button(label_cat, use_container_width=True):
                st.session_state.mostrar_catalogo = not st.session_state.mostrar_catalogo
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Catálogo de productos ─────────────────────────────────
    # Se muestra u oculta con el botón de arriba
    # Permite buscar productos y agregarlos al detalle de la OC
    if st.session_state.mostrar_catalogo and not st.session_state.guardada:
        productos = cargar_productos()
        st.markdown('<div class="card"><div class="card-title blue">🗂️ Catálogo de Productos</div>', unsafe_allow_html=True)

        busqueda = st.text_input(
            "🔎 Buscar",
            value=st.session_state.busqueda_cat,
            placeholder="Nombre, código o categoría...",
            key="buscador_cat"
        )
        st.session_state.busqueda_cat = busqueda

        # Filtra productos en tiempo real según lo que escribe el usuario
        prods_filtrados = [
            p for p in productos
            if busqueda.lower() in p["nombre"].lower()
            or busqueda.lower() in p["codigo"].lower()
            or busqueda.lower() in (p["categoria"]["nombre"].lower() if p.get("categoria") else "")
        ] if busqueda else productos

        if prods_filtrados:
            hc = st.columns([1, 2.5, 0.8, 1.3, 0.9, 1.1, 1])
            for col, h in zip(hc, ["Código", "Nombre", "Und.", "Categoría", "Cantidad", "Precio Unit.", "Acción"]):
                col.markdown(
                    f"<span style='font-size:10px;font-weight:800;color:#64748b;text-transform:uppercase;letter-spacing:0.6px;'>{h}</span>",
                    unsafe_allow_html=True
                )
            st.markdown("<hr>", unsafe_allow_html=True)

            for p in prods_filtrados:
                rc = st.columns([1, 2.5, 0.8, 1.3, 0.9, 1.1, 1])
                rc[0].markdown(f"<span class='item-code'>{p['codigo']}</span>", unsafe_allow_html=True)
                rc[1].write(p["nombre"])
                rc[2].write(p["unidad"])
                rc[3].write(p["categoria"]["nombre"] if p.get("categoria") else "—")

                cant = rc[4].number_input(
                    "Cant.", min_value=1, value=1,
                    key=f"cant_{p['id']}", label_visibility="collapsed"
                )
                precio = rc[5].number_input(
                    "Precio", min_value=0.0, value=float(p["precio_unitario"]),
                    step=0.01, format="%.2f",
                    key=f"precio_{p['id']}", label_visibility="collapsed"
                )

                if rc[6].button("＋ Agregar", key=f"cat_{p['id']}"):
                    # Verifica si el producto ya fue agregado antes de duplicarlo
                    existe = next((d for d in st.session_state.detalle if d["id_producto"] == p["id"]), None)
                    if existe:
                        st.toast(f"⚠️ '{p['nombre']}' ya está en el detalle. Elimínalo si quieres cambiarlo.", icon="⚠️")
                    else:
                        st.session_state.detalle.append({
                            "id_producto":     p["id"],
                            "codigo":          p["codigo"],
                            "nombre":          p["nombre"],
                            "unidad":          p["unidad"],
                            "cantidad":        cant,
                            "precio_unitario": precio,
                        })
                        st.toast(f"✅ Agregado: {p['nombre']} x{cant} @ S/ {precio:.2f}", icon="📦")
                    st.rerun()
        else:
            st.info("⚠️ No se encontraron productos con esa búsqueda.")

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Detalle de la orden ───────────────────────────────────
    # Muestra los productos que el usuario ha ido agregando al catálogo
    # Una vez guardada la OC, los ítems quedan en solo lectura
    st.markdown('<div class="card"><div class="card-title orange">📄 Detalle de la Orden</div>', unsafe_allow_html=True)

    if not st.session_state.detalle:
        st.markdown(
            "<p class='empty-msg'>Sin ítems — usa el botón <b>«Agregar productos del catálogo»</b> para añadir productos</p>",
            unsafe_allow_html=True
        )
    else:
        hd = st.columns([0.35, 0.9, 3, 0.7, 1.1, 1.2, 1.3, 0.7])
        for col, h in zip(hd, ["#", "Código", "Descripción", "Und.", "Cantidad", "P. Unitario", "Subtotal", "Eliminar"]):
            col.markdown(
                f"<span style='font-size:10px;font-weight:800;color:#64748b;text-transform:uppercase;letter-spacing:0.6px;'>{h}</span>",
                unsafe_allow_html=True
            )
        st.markdown("<hr>", unsafe_allow_html=True)

        indices_borrar = []
        for i, item in enumerate(st.session_state.detalle):
            cd = st.columns([0.35, 0.9, 3, 0.7, 1.1, 1.2, 1.3, 0.7])
            cd[0].markdown(f"<span style='color:#94a3b8;font-size:13px;'>{i+1}</span>", unsafe_allow_html=True)
            cd[1].markdown(f"<span class='item-code'>{item['codigo'] or '—'}</span>", unsafe_allow_html=True)
            cd[2].write(item["nombre"])
            cd[3].write(item["unidad"])
            cd[4].markdown(f"<span style='font-weight:700;color:#1e293b;'>{int(item['cantidad'])}</span>", unsafe_allow_html=True)
            cd[5].markdown(f"<span style='color:#475569;'>S/ {item['precio_unitario']:.2f}</span>", unsafe_allow_html=True)

            sub = item["cantidad"] * item["precio_unitario"]
            cd[6].markdown(f"<span class='item-sub'>S/ {sub:,.2f}</span>", unsafe_allow_html=True)

            if not st.session_state.guardada:
                if cd[7].button("🗑️", key=f"rm_{i}", help="Eliminar este ítem"):
                    indices_borrar.append(i)
            else:
                cd[7].markdown("<span style='color:#cbd5e1;'>—</span>", unsafe_allow_html=True)

        # Se eliminan los ítems marcados (en orden inverso para no alterar los índices)
        for idx in reversed(indices_borrar):
            st.session_state.detalle.pop(idx)
        if indices_borrar:
            st.toast("🗑️ Ítem eliminado", icon="🗑️")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Cálculo de totales ────────────────────────────────────
    # Subtotal = suma de (cantidad × precio) de cada ítem
    # IGV = 18% del subtotal (impuesto peruano)
    # Total = subtotal + IGV
    subtotal_val = sum(d["cantidad"] * d["precio_unitario"] for d in st.session_state.detalle)
    igv_val      = subtotal_val * 0.18
    total_val    = subtotal_val + igv_val

    col_res, col_tot = st.columns(2)

    with col_res:
        st.markdown('<div class="card"><div class="card-title green">📊 Resumen</div>', unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        r1.metric("Total ítems",    len(st.session_state.detalle))
        r2.metric("Total unidades", int(sum(d["cantidad"] for d in st.session_state.detalle)))
        st.caption("🔔 Kardex e inventario se trabajarán en la siguiente fase.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_tot:
        st.markdown('<div class="card"><div class="card-title orange">💰 Totales</div>', unsafe_allow_html=True)
        t1, t2 = st.columns(2)
        t1.metric("Subtotal (sin IGV)", f"S/ {subtotal_val:,.2f}")
        t2.metric("IGV (18%)",          f"S/ {igv_val:,.2f}")
        st.markdown(f"""
        <div class="total-box">
            <div class="lbl">TOTAL ORDEN DE COMPRA</div>
            <div class="val">S/ {total_val:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:24px;'></div>", unsafe_allow_html=True)

    # ── Guardar OC en base de datos ───────────────────────────
    # Primero inserta la cabecera en "orden_compra"
    # Luego inserta cada ítem del detalle en "detalle_orden"
    if guardar_click:
        if not prov_sel:
            st.error("⚠️ Debes seleccionar un proveedor antes de guardar.")
        elif not st.session_state.detalle:
            st.error("⚠️ Agrega al menos un producto al detalle de la orden.")
        else:
            try:
                res_oc = sb.table("orden_compra").insert({
                    "numero":       st.session_state.oc_numero,
                    "id_proveedor": prov_sel["id"],
                    "fecha":        str(fecha_oc),
                    "estado":       "PENDIENTE",
                }).execute()

                if res_oc.data:
                    oc = res_oc.data[0]
                    st.session_state.oc_id    = oc["id"]
                    st.session_state.estado   = "PENDIENTE"
                    st.session_state.guardada = True
                    st.session_state.mostrar_catalogo = False

                    # Inserta todos los ítems del detalle de una sola vez (más eficiente)
                    items = [
                        {
                            "id_orden":        oc["id"],
                            "id_producto":     d["id_producto"],
                            "cantidad":        d["cantidad"],
                            "precio_unitario": d["precio_unitario"],
                        }
                        for d in st.session_state.detalle if d["id_producto"]
                    ]
                    if items:
                        sb.table("detalle_orden").insert(items).execute()

                    st.success(f"✅ Orden **{oc['numero']}** guardada correctamente.")
                    st.rerun()
                else:
                    st.error("❌ Error al guardar la orden. Respuesta vacía de Supabase.")
            except Exception as e:
                st.error(f"❌ Error inesperado: {e}")

    if aprobar_click and st.session_state.oc_id:
        try:
            sb.table("orden_compra").update({"estado": "APROBADA"}).eq("id", st.session_state.oc_id).execute()
            st.session_state.estado = "APROBADA"
            st.success("✅ Orden aprobada correctamente.")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al aprobar: {e}")

    if anular_click and st.session_state.oc_id:
        try:
            sb.table("orden_compra").update({"estado": "ANULADA"}).eq("id", st.session_state.oc_id).execute()
            st.session_state.estado = "ANULADA"
            st.warning("❌ Orden anulada.")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al anular: {e}")

# ═══════════════════════════════════════════════════════════════
# TAB 2 — CONSULTA DE ÓRDENES
# ═══════════════════════════════════════════════════════════════
with tab2:

    st.markdown("<div style='margin-bottom:4px;'></div>", unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title blue">🔎 Filtros de búsqueda</div>', unsafe_allow_html=True)

    numeros_ordenes = cargar_numeros_ordenes()
    opciones_numero = ["— Todas —"] + numeros_ordenes

    f1, f2, f3, f4 = st.columns([1.5, 1.5, 1, 1])
    with f1:
        sel_numero = st.selectbox(
            f"N° Orden  ({len(numeros_ordenes)} disponibles)",
            options=opciones_numero,
            key="f_numero"
        )
        filtro_numero = "" if sel_numero == "— Todas —" else sel_numero
    with f2:
        proveedores_c = cargar_proveedores()
        opciones_prov_c = ["— Todos —"] + [f"{p['ruc']} — {p['nombre']}" for p in proveedores_c]
        filtro_prov = st.selectbox("Proveedor", opciones_prov_c, key="f_prov")
    with f3:
        filtro_estado = st.selectbox("Estado", ["— Todos —", "PENDIENTE", "APROBADA", "ANULADA"], key="f_estado")
    with f4:
        filtro_fecha = st.date_input("Fecha desde", value=None, key="f_fecha")

    col_buscar, col_limpiar, _ = st.columns([1, 1, 5])
    buscar_click  = col_buscar.button("🔍 Buscar", type="primary", use_container_width=True, key="btn_buscar")
    limpiar_click = col_limpiar.button("🗑️ Limpiar", use_container_width=True, key="btn_limpiar")

    if limpiar_click:
        for k in ["f_numero", "f_prov", "f_estado", "f_fecha"]:
            if k in st.session_state:
                del st.session_state[k]
        cargar_numeros_ordenes.clear()
        st.session_state["consulta_activa"] = False
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Resultados de búsqueda ────────────────────────────────
    # La consulta se mantiene activa mientras el usuario no limpie los filtros
    if buscar_click or st.session_state.get("consulta_activa"):
        st.session_state["consulta_activa"] = True
        try:
            # Construye la consulta dinámicamente según los filtros activos
            query = sb.table("orden_compra").select(
                "id,numero,fecha,estado,id_proveedor,proveedor:id_proveedor(nombre,ruc)"
            ).order("fecha", desc=True)

            if filtro_numero:
                query = query.eq("numero", filtro_numero)
            if filtro_estado != "— Todos —":
                query = query.eq("estado", filtro_estado)
            if filtro_fecha:
                query = query.gte("fecha", str(filtro_fecha))

            res_consulta = query.execute()
            ordenes = res_consulta.data or []

            # Filtro por proveedor se hace en Python porque Supabase
            # no permite filtros en relaciones fácilmente desde el cliente
            if filtro_prov != "— Todos —":
                ruc_sel = filtro_prov.split(" — ")[0]
                ordenes = [o for o in ordenes if o.get("proveedor", {}).get("ruc") == ruc_sel]

            st.markdown(
                f'<div class="card"><div class="card-title orange">📋 Resultados — {len(ordenes)} orden(es) encontrada(s)</div>',
                unsafe_allow_html=True
            )

            if not ordenes:
                st.markdown("<p class='empty-msg'>No se encontraron órdenes con esos filtros.</p>", unsafe_allow_html=True)
            else:
                hh = st.columns([1.5, 1, 2, 1.2, 1, 1])
                for col, h in zip(hh, ["N° Orden", "Fecha", "Proveedor", "Estado", "Ver detalle", "Acción"]):
                    col.markdown(
                        f"<span style='font-size:10px;font-weight:800;color:#64748b;text-transform:uppercase;letter-spacing:0.6px;'>{h}</span>",
                        unsafe_allow_html=True
                    )
                st.markdown("<hr>", unsafe_allow_html=True)

                for oc in ordenes:
                    ro = st.columns([1.5, 1, 2, 1.2, 1, 1])
                    ro[0].markdown(f"<span style='font-family:monospace;font-weight:700;color:#1e3a5f;'>{oc['numero']}</span>", unsafe_allow_html=True)
                    ro[1].write(oc["fecha"])
                    prov_nombre = oc.get("proveedor", {}).get("nombre", "—") if oc.get("proveedor") else "—"
                    ro[2].write(prov_nombre)

                    badge_c = {"PENDIENTE": "badge-pendiente", "APROBADA": "badge-aprobada", "ANULADA": "badge-anulada"}.get(oc["estado"], "badge-pendiente")
                    ro[3].markdown(f"<span class='badge {badge_c}'>{oc['estado']}</span>", unsafe_allow_html=True)

                    if ro[4].button("👁️ Ver", key=f"ver_{oc['id']}"):
                        st.session_state["oc_detalle_id"]     = oc["id"]
                        st.session_state["oc_detalle_numero"] = oc["numero"]

                    # Acciones rápidas: aprobar o anular directamente desde la lista
                    if oc["estado"] == "PENDIENTE":
                        if ro[5].button("✅", key=f"ap_{oc['id']}", help="Aprobar"):
                            sb.table("orden_compra").update({"estado": "APROBADA"}).eq("id", oc["id"]).execute()
                            st.toast(f"✅ Orden {oc['numero']} aprobada", icon="✅")
                            st.session_state["consulta_activa"] = True
                            st.rerun()
                    elif oc["estado"] == "APROBADA":
                        if ro[5].button("❌", key=f"an_{oc['id']}", help="Anular"):
                            sb.table("orden_compra").update({"estado": "ANULADA"}).eq("id", oc["id"]).execute()
                            st.toast(f"❌ Orden {oc['numero']} anulada", icon="❌")
                            st.session_state["consulta_activa"] = True
                            st.rerun()
                    else:
                        ro[5].markdown("<span style='color:#cbd5e1;'>—</span>", unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # ── Detalle de orden seleccionada ─────────────────
            if st.session_state.get("oc_detalle_id"):
                oc_id_sel  = st.session_state["oc_detalle_id"]
                oc_num_sel = st.session_state.get("oc_detalle_numero", "")

                res_det = sb.table("detalle_orden").select(
                    "id,cantidad,precio_unitario,subtotal,producto:id_producto(codigo,nombre,unidad)"
                ).eq("id_orden", oc_id_sel).execute()
                items_det = res_det.data or []

                st.markdown(
                    f'<div class="card"><div class="card-title green">📄 Detalle — {oc_num_sel}</div>',
                    unsafe_allow_html=True
                )

                if not items_det:
                    st.markdown("<p class='empty-msg'>Esta orden no tiene ítems registrados.</p>", unsafe_allow_html=True)
                else:
                    hdet = st.columns([1, 3, 0.8, 1, 1.2, 1.3])
                    for col, h in zip(hdet, ["Código", "Producto", "Und.", "Cantidad", "P. Unitario", "Subtotal"]):
                        col.markdown(
                            f"<span style='font-size:10px;font-weight:800;color:#64748b;text-transform:uppercase;letter-spacing:0.6px;'>{h}</span>",
                            unsafe_allow_html=True
                        )
                    st.markdown("<hr>", unsafe_allow_html=True)

                    total_det = 0
                    for d in items_det:
                        prod = d.get("producto") or {}
                        rd = st.columns([1, 3, 0.8, 1, 1.2, 1.3])
                        rd[0].markdown(f"<span class='item-code'>{prod.get('codigo', '—')}</span>", unsafe_allow_html=True)
                        rd[1].write(prod.get("nombre", "—"))
                        rd[2].write(prod.get("unidad", "—"))
                        rd[3].markdown(f"<span style='font-weight:700;'>{int(d['cantidad'])}</span>", unsafe_allow_html=True)
                        rd[4].markdown(f"S/ {float(d['precio_unitario']):.2f}")
                        sub = float(d.get("subtotal") or d['cantidad'] * d['precio_unitario'])
                        rd[5].markdown(f"<span class='item-sub'>S/ {sub:,.2f}</span>", unsafe_allow_html=True)
                        total_det += sub

                    st.markdown("<hr>", unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="total-box"><div class="lbl">TOTAL ORDEN</div><div class="val">S/ {total_det:,.2f}</div></div>',
                        unsafe_allow_html=True
                    )

                st.markdown('</div>', unsafe_allow_html=True)

                if st.button("✖️ Cerrar detalle", key="cerrar_det"):
                    del st.session_state["oc_detalle_id"]
                    st.rerun()

        except Exception as e:
            st.error(f"❌ Error al consultar: {e}")
    else:
        st.markdown(
            "<p class='empty-msg'>Usa los filtros de arriba y presiona <b>Buscar</b> para ver las órdenes.</p>",
            unsafe_allow_html=True
        )

# ═══════════════════════════════════════════════════════════════
# TAB 3 — MOVIMIENTOS DE INVENTARIO
# ═══════════════════════════════════════════════════════════════
with tab3:

    # Define qué tipos de movimiento suman (entradas) y cuáles restan (salidas) al stock
    TIPOS_ENTRADA = ["COMPRA", "DEVOLUCION"]
    TIPOS_SALIDA  = ["VENTA", "INHABILITADO", "USO_INTERNO"]
    TODOS_TIPOS   = TIPOS_ENTRADA + TIPOS_SALIDA

    # Etiquetas visuales con emojis para mostrar en los selectores
    MOTIVO_LABEL = {
        "COMPRA":       "🟢 Compra",
        "DEVOLUCION":   "🔵 Devolución",
        "VENTA":        "🔴 Venta",
        "INHABILITADO": "⚫ Inhabilitado",
        "USO_INTERNO":  "🟠 Uso interno",
    }

    st.markdown("<div style='margin-bottom:4px;'></div>", unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title purple">🔄 Registrar Movimiento</div>', unsafe_allow_html=True)

    productos_mov = cargar_productos()
    prod_map_mov  = {f"{p['codigo']} — {p['nombre']}": p for p in productos_mov}
    opciones_prod_mov = ["— Seleccionar producto —"] + list(prod_map_mov.keys())

    m1, m2, m3 = st.columns([1.5, 1.5, 1])
    with m1:
        tipo_mov = st.selectbox(
            "Tipo de movimiento",
            ["— Seleccionar —"] + [MOTIVO_LABEL[t] for t in TODOS_TIPOS],
            key="mov_tipo"
        )
        # Convierte la etiqueta visual de vuelta al valor real para guardar en BD
        tipo_real  = next((t for t in TODOS_TIPOS if MOTIVO_LABEL.get(t) == tipo_mov), None)
        es_entrada = tipo_real in TIPOS_ENTRADA
    with m2:
        prod_sel_label = st.selectbox("Producto", opciones_prod_mov, key="mov_producto")
        prod_sel_mov   = prod_map_mov.get(prod_sel_label)
    with m3:
        fecha_mov = st.date_input("Fecha", value=date.today(), key="mov_fecha")

    m4, m5, m6 = st.columns([1, 1.5, 2])
    with m4:
        cantidad_mov = st.number_input("Cantidad", min_value=1, value=1, key="mov_cantidad")
    with m5:
        # El label cambia según si es entrada o salida
        label_persona = "Recibido de" if es_entrada else "Entregado a"
        persona_mov = st.text_input(f"{label_persona} (persona/área)", placeholder="Nombre...", key="mov_persona")
    with m6:
        observacion_mov = st.text_area("Observación", placeholder="Detalle adicional (opcional)...",
                                       height=68, key="mov_obs")

    # Si el movimiento es una COMPRA, permite vincularlo a una Orden de Compra existente
    id_orden_mov = None
    if tipo_real == "COMPRA":
        numeros_oc  = cargar_numeros_ordenes()
        oc_sel_lbl  = st.selectbox("Vincular a Orden de Compra (opcional)",
                                   ["— Sin vincular —"] + numeros_oc, key="mov_oc")
        if oc_sel_lbl != "— Sin vincular —":
            res_oid = sb.table("orden_compra").select("id").eq("numero", oc_sel_lbl).execute()
            if res_oid.data:
                id_orden_mov = res_oid.data[0]["id"]

    col_gmov, _ = st.columns([1, 5])
    guardar_mov  = col_gmov.button("💾 Registrar", type="primary", use_container_width=True, key="btn_gmov")

    if guardar_mov:
        errores = []
        if not tipo_real:            errores.append("Selecciona el tipo de movimiento.")
        if not prod_sel_mov:         errores.append("Selecciona un producto.")
        if not persona_mov.strip():  errores.append("Indica la persona o área de contacto.")
        if errores:
            for e in errores: st.error(f"⚠️ {e}")
        else:
            try:
                sb.table("movimiento").insert({
                    "fecha":            str(fecha_mov),
                    "tipo":             tipo_real,
                    "motivo":           tipo_real,
                    "cantidad":         cantidad_mov,
                    "id_producto":      prod_sel_mov["id"],
                    "persona_contacto": persona_mov.strip(),
                    "observacion":      observacion_mov.strip() or None,
                    "id_orden":         id_orden_mov,
                }).execute()
                # Limpia el caché de stock y kardex para que se recalculen con el nuevo movimiento
                cargar_stock_actual.clear()
                cargar_kardex.clear()
                st.toast(f"✅ {MOTIVO_LABEL[tipo_real]} — {prod_sel_mov['nombre']} x{cantidad_mov}", icon="✅")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error al registrar: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Historial de movimientos ──────────────────────────────
    st.markdown('<div class="card"><div class="card-title blue">📋 Historial de Movimientos</div>', unsafe_allow_html=True)

    hf1, hf2, hf3, hf4, hf5 = st.columns([1.5, 1.5, 1, 1, 0.8])
    with hf1:
        filtro_tipo_h = st.selectbox("Tipo", ["— Todos —"] + [MOTIVO_LABEL[t] for t in TODOS_TIPOS], key="hf_tipo")
        tipo_filtro_real = next((t for t in TODOS_TIPOS if MOTIVO_LABEL.get(t) == filtro_tipo_h), None)
    with hf2:
        filtro_prod_h  = st.text_input("Buscar producto", placeholder="Nombre o código...", key="hf_prod")
    with hf3:
        filtro_desde_h = st.date_input("Desde", value=None, key="hf_desde")
    with hf4:
        filtro_hasta_h = st.date_input("Hasta", value=None, key="hf_hasta")
    with hf5:
        st.markdown("<div style='margin-top:26px;'></div>", unsafe_allow_html=True)
        buscar_mov_h = st.button("🔍 Filtrar", type="primary", use_container_width=True, key="btn_filtrar_mov")

    if buscar_mov_h or st.session_state.get("mov_historial_activo"):
        st.session_state["mov_historial_activo"] = True
        try:
            query_h = sb.table("movimiento").select(
                "id,fecha,tipo,cantidad,persona_contacto,observacion,"
                "producto:id_producto(codigo,nombre,unidad),"
                "orden:id_orden(numero)"
            ).order("fecha", desc=True).order("created_at", desc=True)

            if tipo_filtro_real:
                query_h = query_h.eq("tipo", tipo_filtro_real)
            if filtro_desde_h:
                query_h = query_h.gte("fecha", str(filtro_desde_h))
            if filtro_hasta_h:
                query_h = query_h.lte("fecha", str(filtro_hasta_h))

            movs = query_h.execute().data or []

            # Filtro por producto se hace en Python (búsqueda de texto libre)
            if filtro_prod_h:
                movs = [m for m in movs if
                        filtro_prod_h.lower() in (m.get("producto") or {}).get("nombre","").lower() or
                        filtro_prod_h.lower() in (m.get("producto") or {}).get("codigo","").lower()]

            entradas = [m for m in movs if m["tipo"] in TIPOS_ENTRADA]
            salidas  = [m for m in movs if m["tipo"] in TIPOS_SALIDA]

            # Métricas resumen del historial filtrado
            sm1, sm2, sm3, sm4 = st.columns(4)
            sm1.metric("Total movimientos", len(movs))
            sm2.metric("📥 Entradas", len(entradas))
            sm3.metric("📤 Salidas",  len(salidas))
            sm4.metric("Unidades netas",
                int(sum(m["cantidad"] for m in entradas) - sum(m["cantidad"] for m in salidas)))
            st.markdown("<hr>", unsafe_allow_html=True)

            if not movs:
                st.markdown("<p class='empty-msg'>No hay movimientos con esos filtros.</p>", unsafe_allow_html=True)
            else:
                widths = [0.8, 1.4, 2.2, 0.6, 0.85, 1.6, 1.2, 2]
                hrow   = st.columns(widths)
                for col, h in zip(hrow, ["Fecha","Tipo","Producto","Und.","Cantidad","Persona / Área","OC","Observación"]):
                    col.markdown(f"<span style='font-size:10px;font-weight:800;color:#64748b;"
                                 f"text-transform:uppercase;letter-spacing:0.6px;'>{h}</span>",
                                 unsafe_allow_html=True)
                st.markdown("<hr style='margin:4px 0 8px;'>", unsafe_allow_html=True)

                for mv in movs:
                    prod  = mv.get("producto") or {}
                    orden = mv.get("orden") or {}
                    es_e  = mv["tipo"] in TIPOS_ENTRADA
                    fila  = st.columns(widths)
                    fila[0].write(mv["fecha"])
                    badge_cls = "badge-entrada" if es_e else "badge-salida"
                    fila[1].markdown(f"<span class='badge {badge_cls}'>{MOTIVO_LABEL.get(mv['tipo'], mv['tipo'])}</span>",
                                     unsafe_allow_html=True)
                    fila[2].write(prod.get("nombre","—"))
                    fila[3].write(prod.get("unidad","—"))
                    signo = "+" if es_e else "-"
                    cls   = "mov-entrada" if es_e else "mov-salida"
                    fila[4].markdown(f"<span class='{cls}'>{signo}{int(mv['cantidad'])}</span>", unsafe_allow_html=True)
                    fila[5].write(mv.get("persona_contacto") or "—")
                    fila[6].markdown(f"<span style='font-family:monospace;font-size:12px;color:#1e3a5f;'>"
                                     f"{orden.get('numero','—')}</span>", unsafe_allow_html=True)
                    fila[7].write(mv.get("observacion") or "—")

        except Exception as e:
            st.error(f"❌ Error al cargar movimientos: {e}")
    else:
        st.markdown("<p class='empty-msg'>Presiona <b>Filtrar</b> para ver el historial.</p>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# TAB 4 — KARDEX & STOCK
# ═══════════════════════════════════════════════════════════════
with tab4:

    MOTIVO_LABEL_K = {
        "COMPRA":       "🟢 Compra",
        "DEVOLUCION":   "🔵 Devolución",
        "VENTA":        "🔴 Venta",
        "INHABILITADO": "⚫ Inhabilitado",
        "USO_INTERNO":  "🟠 Uso interno",
    }

    st.markdown("<div style='margin-bottom:4px;'></div>", unsafe_allow_html=True)

    # ── Stock general de todos los productos ──────────────────
    # Muestra el stock actual calculado desde los movimientos
    # Resalta en rojo los productos con stock bajo o en cero
    st.markdown('<div class="card"><div class="card-title teal">🏬 Stock General — Todos los Productos</div>',
                unsafe_allow_html=True)

    if st.button("🔄 Actualizar stock", key="btn_refresh_stock"):
        # Fuerza recalcular el stock borrando el caché
        cargar_stock_actual.clear()
        cargar_kardex.clear()
        st.rerun()

    try:
        stock_data = cargar_stock_actual()

        if not stock_data:
            st.markdown("<p class='empty-msg'>No hay productos con movimientos registrados aún.</p>",
                        unsafe_allow_html=True)
        else:
            total_prods  = len(stock_data)
            stock_bajo   = [s for s in stock_data if int(s["stock_actual"]) <= int(s.get("stock_minimo") or 0) and int(s["stock_actual"]) > 0]
            sin_stock    = [s for s in stock_data if int(s["stock_actual"]) <= 0]
            ok_stock     = [s for s in stock_data if int(s["stock_actual"]) > int(s.get("stock_minimo") or 0)]

            g1, g2, g3, g4 = st.columns(4)
            g1.metric("Total productos", total_prods)
            g2.metric("✅ Stock OK",     len(ok_stock))
            g3.metric("⚠️ Stock bajo",   len(stock_bajo))
            g4.metric("❌ Sin stock",    len(sin_stock))

            # Alerta visual para productos críticos (stock bajo o sin stock)
            criticos = stock_bajo + sin_stock
            if criticos:
                st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                alerta_txt = " &nbsp;|&nbsp; ".join(
                    f"<span class='alerta-bajo'>⚠️ {s['nombre']} — stock: {int(s['stock_actual'])} (mín: {int(s.get('stock_minimo') or 0)})</span>"
                    for s in criticos
                )
                st.markdown(f"<div style='padding:8px 0;'>{alerta_txt}</div>", unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)

            categorias_st = sorted(set(s.get("categoria") or "Sin categoría" for s in stock_data))
            cat_sel = st.selectbox("Filtrar por categoría", ["— Todas —"] + categorias_st, key="st_cat")
            stock_filtrado = stock_data if cat_sel == "— Todas —" else \
                             [s for s in stock_data if (s.get("categoria") or "Sin categoría") == cat_sel]

            ws = [0.8, 2.5, 0.7, 1.2, 1.1, 1.1, 1.1, 1.2, 1.2]
            hw = st.columns(ws)
            for col, h in zip(hw, ["Código","Producto","Und.","Categoría",
                                    "Entradas","Salidas","Stock actual","Stock mín.","Estado"]):
                col.markdown(f"<span style='font-size:10px;font-weight:800;color:#64748b;"
                             f"text-transform:uppercase;letter-spacing:0.6px;'>{h}</span>",
                             unsafe_allow_html=True)
            st.markdown("<hr style='margin:4px 0 8px;'>", unsafe_allow_html=True)

            for s in stock_filtrado:
                stock_act = int(s["stock_actual"])
                stock_min = int(s.get("stock_minimo") or 0)
                fila      = st.columns(ws)

                fila[0].markdown(f"<span class='item-code'>{s['codigo']}</span>", unsafe_allow_html=True)
                fila[1].write(s["nombre"])
                fila[2].write(s["unidad"])
                fila[3].write(s.get("categoria") or "—")
                fila[4].markdown(f"<span class='mov-entrada'>+{int(s['total_entradas'])}</span>", unsafe_allow_html=True)
                fila[5].markdown(f"<span class='mov-salida'>-{int(s['total_salidas'])}</span>",  unsafe_allow_html=True)

                # Color del stock según si está OK, bajo o en cero
                if stock_act <= 0:
                    fila[6].markdown(f"<span class='stock-cero'>{stock_act}</span>", unsafe_allow_html=True)
                elif stock_act <= stock_min:
                    fila[6].markdown(f"<span class='stock-bajo'>{stock_act}</span>", unsafe_allow_html=True)
                else:
                    fila[6].markdown(f"<span class='stock-ok'>{stock_act}</span>", unsafe_allow_html=True)

                fila[7].write(stock_min if stock_min > 0 else "—")

                if stock_act <= 0:
                    fila[8].markdown("<span class='badge badge-salida'>❌ Sin stock</span>", unsafe_allow_html=True)
                elif stock_act <= stock_min:
                    fila[8].markdown("<span class='alerta-bajo'>⚠️ Bajo</span>", unsafe_allow_html=True)
                else:
                    fila[8].markdown("<span class='badge badge-entrada'>✅ OK</span>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error al cargar stock: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Kardex por producto ────────────────────────────────────
    # Muestra el historial completo de movimientos de un producto
    # con el saldo acumulado después de cada movimiento
    st.markdown('<div class="card"><div class="card-title purple">📒 Kardex por Producto</div>',
                unsafe_allow_html=True)

    productos_kd  = cargar_productos()
    prod_map_kd   = {f"{p['codigo']} — {p['nombre']}": p for p in productos_kd}
    prod_kd_label = st.selectbox("Selecciona un producto para ver su Kardex",
                                 ["— Seleccionar —"] + list(prod_map_kd.keys()),
                                 key="kd_prod_sel")
    prod_kd = prod_map_kd.get(prod_kd_label)

    if prod_kd:
        try:
            kardex_rows = cargar_kardex(prod_kd["id"])

            if not kardex_rows:
                st.markdown("<p class='empty-msg'>Este producto no tiene movimientos registrados.</p>",
                            unsafe_allow_html=True)
            else:
                ultimo   = kardex_rows[-1]
                stock_kd = int(ultimo["saldo"])  # el último saldo = stock actual
                st.markdown(f"""
                <div style='display:flex;gap:24px;padding:12px 0 16px;flex-wrap:wrap;'>
                  <div><span style='font-size:11px;color:#64748b;font-weight:700;text-transform:uppercase;'>Producto</span><br>
                       <span style='font-size:16px;font-weight:800;color:#1e3a5f;'>{prod_kd['nombre']}</span></div>
                  <div><span style='font-size:11px;color:#64748b;font-weight:700;text-transform:uppercase;'>Código</span><br>
                       <span style='font-family:monospace;font-size:15px;font-weight:700;color:#475569;'>{prod_kd['codigo']}</span></div>
                  <div><span style='font-size:11px;color:#64748b;font-weight:700;text-transform:uppercase;'>Unidad</span><br>
                       <span style='font-size:15px;font-weight:700;color:#475569;'>{prod_kd['unidad']}</span></div>
                  <div style='margin-left:auto;text-align:right;'>
                       <span style='font-size:11px;color:#64748b;font-weight:700;text-transform:uppercase;'>Stock actual</span><br>
                       <span style='font-size:28px;font-weight:900;color:{"#059669" if stock_kd > 0 else "#dc2626"};'>{stock_kd}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<hr style='margin:0 0 10px;'>", unsafe_allow_html=True)

                wk = [0.4, 0.9, 1.6, 2.5, 1, 1, 1, 1.8, 1.8, 1.5]
                hk = st.columns(wk)
                for col, h in zip(hk, ["#","Fecha","Tipo","Producto / Ref.",
                                        "Entrada","Salida","Saldo","Persona","OC","Observación"]):
                    col.markdown(f"<span style='font-size:10px;font-weight:800;color:#64748b;"
                                 f"text-transform:uppercase;letter-spacing:0.6px;'>{h}</span>",
                                 unsafe_allow_html=True)
                st.markdown("<hr style='margin:4px 0 6px;'>", unsafe_allow_html=True)

                for i, row in enumerate(kardex_rows, 1):
                    es_e    = int(row.get("entrada", 0)) > 0
                    saldo_r = int(row["saldo"])
                    fk      = st.columns(wk)

                    fk[0].markdown(f"<span style='color:#94a3b8;font-size:12px;'>{i}</span>", unsafe_allow_html=True)
                    fk[1].write(row["fecha"])

                    badge_cls = "badge-entrada" if es_e else "badge-salida"
                    fk[2].markdown(f"<span class='badge {badge_cls}'>"
                                   f"{MOTIVO_LABEL_K.get(row['tipo'], row['tipo'])}</span>",
                                   unsafe_allow_html=True)

                    ref = row.get("orden_compra") or row.get("observacion") or "—"
                    fk[3].markdown(f"<span style='font-family:monospace;font-size:12px;color:#475569;'>{ref}</span>",
                                   unsafe_allow_html=True)

                    entrada_v = int(row.get("entrada", 0))
                    if entrada_v:
                        fk[4].markdown(f"<span class='mov-entrada'>+{entrada_v}</span>", unsafe_allow_html=True)
                    else:
                        fk[4].markdown("<span style='color:#cbd5e1;'>—</span>", unsafe_allow_html=True)

                    salida_v = int(row.get("salida", 0))
                    if salida_v:
                        fk[5].markdown(f"<span class='mov-salida'>-{salida_v}</span>", unsafe_allow_html=True)
                    else:
                        fk[5].markdown("<span style='color:#cbd5e1;'>—</span>", unsafe_allow_html=True)

                    # Saldo en verde si hay stock, rojo si está en cero o negativo
                    saldo_cls = "kd-saldo-ok" if saldo_r > 0 else "kd-saldo-bajo"
                    fk[6].markdown(f"<span class='{saldo_cls}'>{saldo_r}</span>", unsafe_allow_html=True)

                    fk[7].write(row.get("persona_contacto") or "—")
                    fk[8].markdown(f"<span style='font-family:monospace;font-size:12px;color:#1e3a5f;'>"
                                   f"{row.get('orden_compra') or '—'}</span>", unsafe_allow_html=True)
                    fk[9].write(row.get("observacion") or "—")

                st.markdown("<hr>", unsafe_allow_html=True)
                color_final = "#059669" if stock_kd > 0 else "#dc2626"
                st.markdown(
                    f"<div class='total-box' style='text-align:left;'>"
                    f"<span class='lbl'>SALDO FINAL</span>&nbsp;&nbsp;"
                    f"<span style='font-size:26px;font-weight:900;color:{color_final};'>"
                    f"{stock_kd} {prod_kd['unidad']}</span></div>",
                    unsafe_allow_html=True
                )

        except Exception as e:
            st.error(f"❌ Error al cargar kardex: {e}")
    else:
        st.markdown("<p class='empty-msg'>Selecciona un producto para ver su kardex detallado.</p>",
                    unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
