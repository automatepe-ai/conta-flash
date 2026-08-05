"""
ContaFlash — Tus declaraciones en segundos
Web app para extracción y consolidación de declaraciones SUNAT.
"""

import streamlit as st
from streamlit_local_storage import LocalStorage
from extractor import process_uploaded_pdfs, consolidate_uploaded_excels

# ============================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================
st.set_page_config(
    page_title="ContaFlash — Tus declaraciones en segundos",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CONTROL DE USO FREEMIUM + CÓDIGOS PRO
# ============================================================
MAX_FREE_USES = 3
USAGE_KEY = "contaflash_usage_count"
PRO_KEY = "contaflash_pro_active"
PRO_CLIENT_KEY = "contaflash_pro_client"

if USAGE_KEY not in st.session_state:
    st.session_state[USAGE_KEY] = 0
if PRO_KEY not in st.session_state:
    st.session_state[PRO_KEY] = False
if PRO_CLIENT_KEY not in st.session_state:
    st.session_state[PRO_CLIENT_KEY] = ""

# Resultados de procesamiento (persisten entre reruns)
PDF_RESULTS_KEY = "contaflash_pdf_results"
EXCEL_RESULTS_KEY = "contaflash_excel_results"
if PDF_RESULTS_KEY not in st.session_state:
    st.session_state[PDF_RESULTS_KEY] = None
if EXCEL_RESULTS_KEY not in st.session_state:
    st.session_state[EXCEL_RESULTS_KEY] = None

# ============================================================
# PERSISTENCIA — localStorage
# ============================================================
_local_storage = LocalStorage()
PERSIST_KEY = "contaflash_state"


def _load_state():
    """Restaura estado desde localStorage al iniciar."""
    saved = _local_storage.getItem(PERSIST_KEY)
    if saved:
        st.session_state[USAGE_KEY] = saved.get("usage", 0)
        st.session_state[PRO_KEY] = saved.get("pro", False)
        st.session_state[PRO_CLIENT_KEY] = saved.get("client", "")


def _save_state():
    """Persiste estado actual a localStorage."""
    _local_storage.setItem(PERSIST_KEY, {
        "usage": st.session_state[USAGE_KEY],
        "pro": st.session_state[PRO_KEY],
        "client": st.session_state[PRO_CLIENT_KEY],
    })


_load_state()


def _get_pro_codes() -> dict:
    """Lee códigos Pro desde st.secrets. Retorna {codigo: nombre_cliente}."""
    try:
        return dict(st.secrets.get("pro_codes", {}))
    except Exception:
        return {}


def validate_pro_code(code: str) -> tuple[bool, str]:
    """Valida un código Pro. Retorna (es_valido, nombre_cliente)."""
    pro_codes = _get_pro_codes()
    code = code.strip()
    if code in pro_codes:
        return True, pro_codes[code]
    return False, ""


def is_pro() -> bool:
    return st.session_state[PRO_KEY]


def check_usage() -> bool:
    """Retorna True si el usuario puede usar la herramienta."""
    if is_pro():
        return True
    return st.session_state[USAGE_KEY] < MAX_FREE_USES


def increment_usage():
    """Incrementa el contador de uso (solo para usuarios free)."""
    if not is_pro():
        st.session_state[USAGE_KEY] += 1
        _save_state()


def remaining_uses() -> int:
    if is_pro():
        return -1  # ilimitado
    return MAX_FREE_USES - st.session_state[USAGE_KEY]


# ============================================================
# ESTILOS CUSTOM — Paleta Crema Corporativa
# ============================================================
st.markdown("""
<style>
    /* === FONDO PRINCIPAL === */
    .stApp {
        background-color: #faf7f2;
    }
    
    /* === HEADER === */
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
    }
    .main-header h1 {
        color: #1e3a5f;
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .main-header p {
        color: #6b6560;
        font-size: 1.1rem;
        margin-top: 0;
    }
    
    /* === BADGE DE USOS === */
    .usage-badge {
        background: #f5f0e8;
        border: 1px solid #e8e0d6;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        text-align: center;
        font-size: 0.9rem;
        margin-bottom: 1.2rem;
        color: #2d2a26;
    }
    
    /* === CARDS === */
    .stat-card {
        background: #ffffff;
        border-left: 4px solid #34d399;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e8e0d6;
    }
    .stat-card.error {
        border-left-color: #ef4444;
    }
    
    /* === BLOQUE DE LÍMITE (mantener ROJO como condición) === */
    .block-message {
        text-align: center;
        padding: 2rem;
        background: #fef2f2;
        border-radius: 12px;
        border: 2px solid #ef4444;
    }
    .block-message h3 {
        color: #dc2626;
    }
    .block-message p {
        color: #2d2a26;
    }
    
    /* === FOOTER OCULTO === */
    footer {visibility: hidden;}
    
    /* === VALIDACIÓN === */
    .validation-section {
        display: flex;
        justify-content: center;
        gap: 2rem;
        flex-wrap: wrap;
        margin: 2rem 0;
    }
    .validation-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        max-width: 300px;
        text-align: left;
        border: 1px solid #e8e0d6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .validation-card p {
        font-size: 0.95rem;
        color: #2d2a26;
        margin-bottom: 0.8rem;
        line-height: 1.5;
    }
    .validation-name {
        font-weight: 600;
        color: #1e3a5f;
        font-size: 0.9rem;
    }
    .validation-role {
        color: #6b6560;
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
    }
    .validation-badge {
        display: inline-block;
        background: #eafaf1;
        color: #27ae60;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }
    .validation-metric {
        text-align: center;
        padding: 1rem;
    }
    .validation-metric .number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a5f;
    }
    .validation-metric .label {
        font-size: 0.9rem;
        color: #6b6560;
        margin-top: 0.3rem;
    }
    
    /* === BOTONES PRIMARIOS (azul oscuro) === */
    .stButton > button[kind="primary"],
    button[data-testid="stBaseButton-primary"] {
        background-color: #1e3a5f;
        border-color: #1e3a5f;
        color: #ffffff;
    }
    .stButton > button[kind="primary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover {
        background-color: #162d4a;
        border-color: #162d4a;
    }
    
    /* === BOTÓN SECUNDARIO (WhatsApp verde) === */
    .stMarkdown a[href*="wa.me"] {
        background-color: #25D366;
        color: #ffffff !important;
        padding: 0.4rem 1rem;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 600;
        transition: background-color 0.2s;
    }
    .stMarkdown a[href*="wa.me"]:hover {
        background-color: #1da851;
    }
    
    /* === SIDEBAR === */
    section[data-testid="stSidebar"] {
        background-color: #f5f0e8;
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #2d2a26;
    }
    
    /* === TABS (estilo sutil) === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: #f5f0e8;
        border-radius: 8px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 500;
        color: #6b6560;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        color: #1e3a5f;
        border-bottom: none;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR: CÓDIGO PRO (Compacto)
# ============================================================
with st.sidebar:
    if is_pro():
        st.success(f"✅ Plan Pro activo — {st.session_state[PRO_CLIENT_KEY]}")
        if st.button("Cerrar sesión Pro", use_container_width=True):
            st.session_state[PRO_KEY] = False
            st.session_state[PRO_CLIENT_KEY] = ""
            _save_state()
            st.rerun()
    else:
        with st.expander("🔑 **Acceso Pro**", expanded=True):
            st.markdown("¿Ya tienes un código?")
            pro_input = st.text_input(
                "Código",
                type="password",
                placeholder="CF-XXXX-XXXX",
                key="pro_code_input",
                label_visibility="collapsed",
            )
            if st.button("Activar", key="btn_activate_pro", use_container_width=True):
                if pro_input:
                    valid, client_name = validate_pro_code(pro_input)
                    if valid:
                        st.session_state[PRO_KEY] = True
                        st.session_state[PRO_CLIENT_KEY] = client_name
                        _save_state()
                        st.rerun()
                    else:
                        st.error("Código inválido.")
                else:
                    st.warning("Ingresa tu código.")
        
        st.markdown("---")
        st.markdown(
            "**¿Acceso ilimitado?**\n\n"
            "📱 [WhatsApp](https://wa.me/51962927872?text=Hola%2C+quiero+un+código+Pro+de+ContaFlash)"
        )

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="main-header">
    <h1>⚡ ContaFlash</h1>
    <p>Tus declaraciones SUNAT en segundos</p>
</div>
""", unsafe_allow_html=True)

# Mostrar usos restantes
uses_left = remaining_uses()
if is_pro():
    st.markdown(
        '<div class="usage-badge" style="background:#eafaf1">'
        '⚡ <strong style="color:#27ae60">Plan Pro — Uso ilimitado</strong></div>',
        unsafe_allow_html=True
    )
elif uses_left > 0:
    color = "#27ae60" if uses_left > 1 else "#e67e22"
    st.markdown(
        f'<div class="usage-badge">Usos gratuitos restantes: '
        f'<strong style="color:{color}">{uses_left} de {MAX_FREE_USES}</strong></div>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        '<div class="usage-badge" style="background:#fdf2e9">'
        'Usos gratuitos agotados — <strong>Contacta para acceso completo</strong></div>',
        unsafe_allow_html=True
    )

# ============================================================
# TABS PRINCIPALES
# ============================================================
tab_pdf, tab_excel, tab_info, tab_validacion = st.tabs([
    "📄 Extraer de PDFs",
    "📁 Consolidar Excels",
    "ℹ️ Información",
    "✅ Validación"
])

# ─────────────────────────────────────────────────────────
# TAB 1: EXTRAER DE PDFs / ZIPs
# ─────────────────────────────────────────────────────────
with tab_pdf:
    st.markdown("### Extrae datos del Formulario 621 desde PDFs")
    st.markdown(
        "Sube archivos **PDF** de declaraciones SUNAT (Formulario 621) "
        "o **ZIPs** que contengan PDFs. Se generará un Excel consolidado "
        "con todas las casillas extraídas."
    )

    uploaded_pdfs = st.file_uploader(
        "Arrastra tus archivos aquí",
        type=["pdf", "zip"],
        accept_multiple_files=True,
        key="pdf_uploader",
        help="Acepta PDFs individuales o archivos ZIP con PDFs dentro"
    )

    if uploaded_pdfs:
        st.info(f"📎 {len(uploaded_pdfs)} archivo(s) seleccionado(s)")

        if not check_usage():
            st.markdown("""
            <div class="block-message">
                <h3>🔒 Límite de uso gratuito alcanzado</h3>
                <p>Has usado tus 3 procesamientos gratuitos.</p>
                <p>Para acceso ilimitado, contáctanos:</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("📱 **WhatsApp:** [Contactar](https://wa.me/51962927872?text=Hola%2C+quiero+acceso+completo+a+ContaFlash)")
            with col2:
                st.markdown("📧 **Email:** hola@contaflash.com")
        else:
            if st.button("🚀 Procesar archivos", key="btn_pdf", type="primary"):
                with st.spinner("Procesando PDFs..."):
                    _results = process_uploaded_pdfs(uploaded_pdfs)
                st.session_state[PDF_RESULTS_KEY] = _results

        # Renderizar resultados desde session_state (persiste entre reruns)
        if st.session_state[PDF_RESULTS_KEY] is not None:
            excel_bytes, stats, logs, df = st.session_state[PDF_RESULTS_KEY]

            # Mostrar logs
            with st.expander("📋 Detalle del procesamiento", expanded=True):
                for log_line in logs:
                    st.text(log_line)

            if excel_bytes:
                increment_usage()

                # Panel de resultados
                n_formularios = stats['ok']
                n_casillas = stats.get('n_casillas', 0)
                n_periodos = len(stats.get('periodos', []))
                n_empresas = len(stats.get('empresas', []))
                n_errores = stats['errors']
                tiempo_ahorrado_min = n_formularios * 30
                horas = tiempo_ahorrado_min // 60
                minutos = tiempo_ahorrado_min % 60
                tiempo_str = f"{horas}h {minutos}min" if horas > 0 else f"{minutos}min"

                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);
                            border-radius:16px;padding:2rem;margin:1rem 0;color:white;">
                    <div style="text-align:center;margin-bottom:1.5rem;">
                        <span style="font-size:2.5rem;">✅</span>
                        <h2 style="color:#e67e22;margin:0.5rem 0 0 0;">Procesamiento completado</h2>
                    </div>
                    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1rem;">
                        <div style="background:rgba(255,255,255,0.1);border-radius:12px;padding:1rem;text-align:center;">
                            <div style="font-size:2rem;font-weight:bold;color:#e67e22;">{n_formularios}</div>
                            <div style="font-size:0.85rem;opacity:0.8;">Formularios</div>
                        </div>
                        <div style="background:rgba(255,255,255,0.1);border-radius:12px;padding:1rem;text-align:center;">
                            <div style="font-size:2rem;font-weight:bold;color:#2ecc71;">{n_casillas}</div>
                            <div style="font-size:0.85rem;opacity:0.8;">Registros extraídos</div>
                        </div>
                        <div style="background:rgba(255,255,255,0.1);border-radius:12px;padding:1rem;text-align:center;">
                            <div style="font-size:2rem;font-weight:bold;color:#3498db;">{n_empresas}</div>
                            <div style="font-size:0.85rem;opacity:0.8;">Empresas</div>
                        </div>
                        <div style="background:rgba(255,255,255,0.1);border-radius:12px;padding:1rem;text-align:center;">
                            <div style="font-size:2rem;font-weight:bold;color:#9b59b6;">{n_periodos}</div>
                            <div style="font-size:0.85rem;opacity:0.8;">Períodos</div>
                        </div>
                    </div>
                    <div style="background:rgba(46,204,113,0.15);border-radius:12px;padding:1rem;margin-top:1rem;text-align:center;">
                        <div style="font-size:0.9rem;opacity:0.8;">Tiempo estimado ahorrado</div>
                        <div style="font-size:1.8rem;font-weight:bold;color:#2ecc71;">⏱️ {tiempo_str}</div>
                        <div style="font-size:0.8rem;opacity:0.6;">vs ~30 min por declaración manual</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Estadísticas del lote
                totales = stats.get('totales', {})
                if any(v != 0 for v in totales.values()):
                    igv_ventas = totales.get('igv_ventas', 0)
                    igv_compras = totales.get('igv_compras', 0)
                    renta = totales.get('renta', 0)

                    def _fmt_soles(val):
                        if val == 0: return "S/ 0"
                        if abs(val) >= 1_000_000: return f"S/ {val/1_000_000:,.1f}M"
                        if abs(val) >= 1_000: return f"S/ {val/1_000:,.1f}K"
                        return f"S/ {val:,.2f}"

                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,#0f3460 0%,#16213e 100%);
                                border-radius:12px;padding:1.5rem;margin:0.5rem 0;color:white;">
                        <div style="text-align:center;margin-bottom:1rem;">
                            <span style="font-size:1.2rem;">📈</span>
                            <strong style="color:#e67e22;"> Estadísticas del Lote</strong>
                        </div>
                        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;">
                            <div style="background:rgba(255,255,255,0.1);border-radius:8px;padding:0.8rem;text-align:center;">
                                <div style="font-size:1.3rem;font-weight:bold;color:#2ecc71;">{_fmt_soles(igv_ventas)}</div>
                                <div style="font-size:0.75rem;opacity:0.7;">IGV Ventas (C101)</div>
                            </div>
                            <div style="background:rgba(255,255,255,0.1);border-radius:8px;padding:0.8rem;text-align:center;">
                                <div style="font-size:1.3rem;font-weight:bold;color:#e74c3c;">{_fmt_soles(igv_compras)}</div>
                                <div style="font-size:0.75rem;opacity:0.7;">IGV Compras (C108)</div>
                            </div>
                            <div style="background:rgba(255,255,255,0.1);border-radius:8px;padding:0.8rem;text-align:center;">
                                <div style="font-size:1.3rem;font-weight:bold;color:#f39c12;">{_fmt_soles(renta)}</div>
                                <div style="font-size:0.75rem;opacity:0.7;">Renta (C312)</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                if n_errores > 0:
                    st.warning(f"⚠️ {n_errores} archivo(s) con errores — revisa el detalle abajo")

                # Validaciones automáticas
                warnings = stats.get('warnings', [])
                if warnings:
                    with st.expander(f"🔍 Validaciones automáticas — {len(warnings)} advertencia(s)", expanded=False):
                        for w in warnings:
                            icon = "⚠️" if w['severidad'] == 'warning' else "ℹ️"
                            st.markdown(f"{icon} **{w['mensaje']}**")

                # Logs
                with st.expander("📋 Detalle del procesamiento", expanded=False):
                    for log_line in logs:
                        st.text(log_line)

                # Botones de descarga
                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    st.download_button(
                        label="📥 Descargar Excel Consolidado",
                        data=excel_bytes,
                        file_name="ContaFlash_621_Consolidado.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                    )
                with col_dl2:
                    if df is not None:
                        csv_bytes = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📄 Descargar CSV",
                            data=csv_bytes,
                            file_name="ContaFlash_621_Consolidado.csv",
                            mime="text/csv",
                        )

                # Consolidación inteligente
                if df is not None and len(df) > 0:
                    st.markdown("---")
                    st.markdown("### 📊 Consolidación Inteligente")
                    st.markdown("Elige cómo quieres ver tus datos:")

                    vista_pdf = st.radio(
                        "Vista de consolidación:",
                        ["📋 General", "🏢 Por RUC", "📅 Por Período", "🏭 Por Empresa", "📆 Por Mes"],
                        key="vista_consolidado_pdf",
                        horizontal=True,
                    )

                    casilla_cols = [c for c in df.columns if c.startswith('C') and c[1:].isdigit()]
                    display_cols = ['RUC', 'Razon_Social', 'Periodo'] + casilla_cols[:5]
                    display_cols = [c for c in display_cols if c in df.columns]

                    if vista_pdf == "📋 General":
                        st.markdown("**Vista general:**")
                        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)

                    elif vista_pdf == "🏢 Por RUC" and 'RUC' in df.columns:
                        st.markdown("**Vista por RUC:**")
                        for ruc in sorted(df['RUC'].dropna().unique()):
                            ruc_df = df[df['RUC'] == ruc]
                            razon = ruc_df['Razon_Social'].iloc[0] if 'Razon_Social' in ruc_df.columns else ''
                            with st.expander(f"🏢 {ruc} — {razon} ({len(ruc_df)} declaración(es))"):
                                st.dataframe(ruc_df[display_cols], use_container_width=True, hide_index=True)

                    elif vista_pdf == "📅 Por Período" and 'Periodo' in df.columns:
                        st.markdown("**Vista por Período:**")
                        for periodo in sorted(df['Periodo'].dropna().unique()):
                            per_df = df[df['Periodo'] == periodo]
                            with st.expander(f"📅 {periodo} ({len(per_df)} declaración(es))"):
                                st.dataframe(per_df[display_cols], use_container_width=True, hide_index=True)

                    elif vista_pdf == "🏭 Por Empresa" and 'Razon_Social' in df.columns:
                        st.markdown("**Vista por Empresa:**")
                        for empresa in sorted(df['Razon_Social'].dropna().unique()):
                            emp_df = df[df['Razon_Social'] == empresa]
                            with st.expander(f"🏭 {empresa} ({len(emp_df)} declaración(es))"):
                                st.dataframe(emp_df[display_cols], use_container_width=True, hide_index=True)

                    elif vista_pdf == "📆 Por Mes" and 'Periodo' in df.columns:
                        st.markdown("**Vista por Mes:**")
                        df['_Mes'] = df['Periodo'].str[:7] if df['Periodo'].str.len() >= 7 else df['Periodo']
                        for mes in sorted(df['_Mes'].dropna().unique()):
                            mes_df = df[df['_Mes'] == mes]
                            with st.expander(f"📆 {mes} ({len(mes_df)} declaración(es))"):
                                st.dataframe(mes_df[display_cols], use_container_width=True, hide_index=True)
                        if '_Mes' in df.columns:
                            df.drop('_Mes', axis=1, inplace=True)

                st.success(f"✅ Te quedan {remaining_uses()} uso(s) gratuito(s).")
                st.markdown(
                    '💡 **¿Tienes otra tarea contable que te quite horas?** '
                    'Cuéntanos y te proponemos una solución. '
                    '[Escríbenos por WhatsApp](https://wa.me/51962927872?text=Hola%2C+uso+ContaFlash+y+tengo+otra+tarea+que+me+quita+tiempo%3A+)'
                )
            else:
                st.error("No se pudieron extraer datos de los archivos proporcionados.")

            # Botón Nueva Carga
            st.markdown("---")
            if st.button("🔄 Nueva Carga", key="btn_new_pdf"):
                st.session_state[PDF_RESULTS_KEY] = None
                st.rerun()


# ─────────────────────────────────────────────────────────
# TAB 2: CONSOLIDAR EXCELS / CSVs
# ─────────────────────────────────────────────────────────
with tab_excel:
    st.markdown("### Consolida archivos Excel/CSV del PDT 621")
    st.markdown(
        "Sube archivos **Excel** o **CSV** exportados del PDT 621 "
        "(con columnas Nro Casilla y Valor Casilla). "
        "Se generará un Excel consolidado con una fila por período."
    )

    empresa_name = st.text_input(
        "Nombre de empresa (opcional)",
        value="Mi Empresa",
        help="Se usará como identificador en el consolidado"
    )

    uploaded_excels = st.file_uploader(
        "Arrastra tus archivos aquí",
        type=["xlsx", "xls", "csv"],
        accept_multiple_files=True,
        key="excel_uploader",
        help="Acepta archivos Excel (.xlsx, .xls) o CSV"
    )

    if uploaded_excels:
        st.info(f"📎 {len(uploaded_excels)} archivo(s) seleccionado(s)")

        if not check_usage():
            st.markdown("""
            <div class="block-message">
                <h3>🔒 Límite de uso gratuito alcanzado</h3>
                <p>Has usado tus 3 procesamientos gratuitos.</p>
                <p>Para acceso ilimitado, contáctanos:</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("📱 **WhatsApp:** [Contactar](https://wa.me/51962927872?text=Hola%2C+quiero+acceso+completo+a+ContaFlash)")
            with col2:
                st.markdown("📧 **Email:** hola@contaflash.com")
        else:
            if st.button("🚀 Consolidar archivos", key="btn_excel", type="primary"):
                with st.spinner("Consolidando..."):
                    _results = consolidate_uploaded_excels(
                        uploaded_excels, empresa_name
                    )
                st.session_state[EXCEL_RESULTS_KEY] = _results

        # Renderizar resultados desde session_state (persiste entre reruns)
        if st.session_state[EXCEL_RESULTS_KEY] is not None:
            excel_bytes, stats, logs, df = st.session_state[EXCEL_RESULTS_KEY]

            with st.expander("📋 Detalle del procesamiento", expanded=True):
                for log_line in logs:
                    st.text(log_line)

            if excel_bytes:
                increment_usage()

                # Panel de resultados
                n_formularios = stats['ok']
                n_casillas = stats.get('n_casillas', 0)
                n_periodos = len(stats.get('periodos', []))
                n_empresas = stats.get('empresas', 1)
                n_errores = stats['errors']
                tiempo_ahorrado_min = n_formularios * 30
                horas = tiempo_ahorrado_min // 60
                minutos = tiempo_ahorrado_min % 60
                tiempo_str = f"{horas}h {minutos}min" if horas > 0 else f"{minutos}min"

                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);
                            border-radius:16px;padding:2rem;margin:1rem 0;color:white;">
                    <div style="text-align:center;margin-bottom:1.5rem;">
                        <span style="font-size:2.5rem;">✅</span>
                        <h2 style="color:#e67e22;margin:0.5rem 0 0 0;">Consolidación completada</h2>
                    </div>
                    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1rem;">
                        <div style="background:rgba(255,255,255,0.1);border-radius:12px;padding:1rem;text-align:center;">
                            <div style="font-size:2rem;font-weight:bold;color:#e67e22;">{n_formularios}</div>
                            <div style="font-size:0.85rem;opacity:0.8;">Formularios</div>
                        </div>
                        <div style="background:rgba(255,255,255,0.1);border-radius:12px;padding:1rem;text-align:center;">
                            <div style="font-size:2rem;font-weight:bold;color:#2ecc71;">{n_casillas}</div>
                            <div style="font-size:0.85rem;opacity:0.8;">Registros extraídos</div>
                        </div>
                        <div style="background:rgba(255,255,255,0.1);border-radius:12px;padding:1rem;text-align:center;">
                            <div style="font-size:2rem;font-weight:bold;color:#3498db;">{n_empresas}</div>
                            <div style="font-size:0.85rem;opacity:0.8;">Empresas</div>
                        </div>
                        <div style="background:rgba(255,255,255,0.1);border-radius:12px;padding:1rem;text-align:center;">
                            <div style="font-size:2rem;font-weight:bold;color:#9b59b6;">{n_periodos}</div>
                            <div style="font-size:0.85rem;opacity:0.8;">Períodos</div>
                        </div>
                    </div>
                    <div style="background:rgba(46,204,113,0.15);border-radius:12px;padding:1rem;margin-top:1rem;text-align:center;">
                        <div style="font-size:0.9rem;opacity:0.8;">Tiempo estimado ahorrado</div>
                        <div style="font-size:1.8rem;font-weight:bold;color:#2ecc71;">⏱️ {tiempo_str}</div>
                        <div style="font-size:0.8rem;opacity:0.6;">vs ~30 min por declaración manual</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Estadísticas del lote
                totales = stats.get('totales', {})
                if any(v != 0 for v in totales.values()):
                    igv_ventas = totales.get('igv_ventas', 0)
                    igv_compras = totales.get('igv_compras', 0)
                    renta = totales.get('renta', 0)

                    def _fmt_soles(val):
                        if val == 0: return "S/ 0"
                        if abs(val) >= 1_000_000: return f"S/ {val/1_000_000:,.1f}M"
                        if abs(val) >= 1_000: return f"S/ {val/1_000:,.1f}K"
                        return f"S/ {val:,.2f}"

                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,#0f3460 0%,#16213e 100%);
                                border-radius:12px;padding:1.5rem;margin:0.5rem 0;color:white;">
                        <div style="text-align:center;margin-bottom:1rem;">
                            <span style="font-size:1.2rem;">📈</span>
                            <strong style="color:#e67e22;"> Estadísticas del Lote</strong>
                        </div>
                        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;">
                            <div style="background:rgba(255,255,255,0.1);border-radius:8px;padding:0.8rem;text-align:center;">
                                <div style="font-size:1.3rem;font-weight:bold;color:#2ecc71;">{_fmt_soles(igv_ventas)}</div>
                                <div style="font-size:0.75rem;opacity:0.7;">IGV Ventas (C101)</div>
                            </div>
                            <div style="background:rgba(255,255,255,0.1);border-radius:8px;padding:0.8rem;text-align:center;">
                                <div style="font-size:1.3rem;font-weight:bold;color:#e74c3c;">{_fmt_soles(igv_compras)}</div>
                                <div style="font-size:0.75rem;opacity:0.7;">IGV Compras (C108)</div>
                            </div>
                            <div style="background:rgba(255,255,255,0.1);border-radius:8px;padding:0.8rem;text-align:center;">
                                <div style="font-size:1.3rem;font-weight:bold;color:#f39c12;">{_fmt_soles(renta)}</div>
                                <div style="font-size:0.75rem;opacity:0.7;">Renta (C312)</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                if n_errores > 0:
                    st.warning(f"⚠️ {n_errores} archivo(s) con errores — revisa el detalle abajo")

                # Validaciones automáticas
                warnings = stats.get('warnings', [])
                if warnings:
                    with st.expander(f"🔍 Validaciones automáticas — {len(warnings)} advertencia(s)", expanded=False):
                        for w in warnings:
                            icon = "⚠️" if w['severidad'] == 'warning' else "ℹ️"
                            st.markdown(f"{icon} **{w['mensaje']}**")

                # Logs
                with st.expander("📋 Detalle del procesamiento", expanded=False):
                    for log_line in logs:
                        st.text(log_line)

                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    st.download_button(
                        label="📥 Descargar Consolidado",
                        data=excel_bytes,
                        file_name="ContaFlash_Consolidado_PDT621.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                    )
                with col_dl2:
                    if df is not None:
                        csv_bytes = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📄 Descargar CSV",
                            data=csv_bytes,
                            file_name="ContaFlash_Consolidado_PDT621.csv",
                            mime="text/csv",
                        )

                # Consolidación inteligente
                if df is not None and len(df) > 0:
                    st.markdown("---")
                    st.markdown("### 📊 Consolidación Inteligente")
                    st.markdown("Elige cómo quieres ver tus datos:")

                    vista_excel = st.radio(
                        "Vista de consolidación:",
                        ["📋 General", "🏢 Por RUC", "📅 Por Período", "🏭 Por Empresa", "📆 Por Mes"],
                        key="vista_consolidado_excel",
                        horizontal=True,
                    )

                    casilla_cols = [c for c in df.columns if c.startswith('C') and c[1:].isdigit()]
                    display_cols = ['RUC', 'Razon_Social', 'Periodo'] + casilla_cols[:5]
                    display_cols = [c for c in display_cols if c in df.columns]

                    if vista_excel == "📋 General":
                        st.markdown("**Vista general:**")
                        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)

                    elif vista_excel == "🏢 Por RUC" and 'RUC' in df.columns:
                        st.markdown("**Vista por RUC:**")
                        for ruc in sorted(df['RUC'].dropna().unique()):
                            ruc_df = df[df['RUC'] == ruc]
                            razon = ruc_df['Razon_Social'].iloc[0] if 'Razon_Social' in ruc_df.columns else ''
                            with st.expander(f"🏢 {ruc} — {razon} ({len(ruc_df)} declaración(es))"):
                                st.dataframe(ruc_df[display_cols], use_container_width=True, hide_index=True)

                    elif vista_excel == "📅 Por Período" and 'Periodo' in df.columns:
                        st.markdown("**Vista por Período:**")
                        for periodo in sorted(df['Periodo'].dropna().unique()):
                            per_df = df[df['Periodo'] == periodo]
                            with st.expander(f"📅 {periodo} ({len(per_df)} declaración(es))"):
                                st.dataframe(per_df[display_cols], use_container_width=True, hide_index=True)

                    elif vista_excel == "🏭 Por Empresa" and 'Razon_Social' in df.columns:
                        st.markdown("**Vista por Empresa:**")
                        for empresa in sorted(df['Razon_Social'].dropna().unique()):
                            emp_df = df[df['Razon_Social'] == empresa]
                            with st.expander(f"🏭 {empresa} ({len(emp_df)} declaración(es))"):
                                st.dataframe(emp_df[display_cols], use_container_width=True, hide_index=True)

                    elif vista_excel == "📆 Por Mes" and 'Periodo' in df.columns:
                        st.markdown("**Vista por Mes:**")
                        df['_Mes'] = df['Periodo'].str[:7] if df['Periodo'].str.len() >= 7 else df['Periodo']
                        for mes in sorted(df['_Mes'].dropna().unique()):
                            mes_df = df[df['_Mes'] == mes]
                            with st.expander(f"📆 {mes} ({len(mes_df)} declaración(es))"):
                                st.dataframe(mes_df[display_cols], use_container_width=True, hide_index=True)
                        if '_Mes' in df.columns:
                            df.drop('_Mes', axis=1, inplace=True)

                st.success(f"✅ Te quedan {remaining_uses()} uso(s) gratuito(s).")
                st.markdown(
                    '💡 **¿Tienes otra tarea contable que te quite horas?** '
                    'Cuéntanos y te proponemos una solución. '
                    '[Escríbenos por WhatsApp](https://wa.me/51962927872?text=Hola%2C+uso+ContaFlash+y+tengo+otra+tarea+que+me+quita+tiempo%3A+)'
                )
            else:
                st.error("No se pudo consolidar. Verifica que los archivos tengan columnas 'Nro Casilla' y 'Valor Casilla'.")

            # Botón Nueva Carga
            st.markdown("---")
            if st.button("🔄 Nueva Carga", key="btn_new_excel"):
                st.session_state[EXCEL_RESULTS_KEY] = None
                st.rerun()



# ─────────────────────────────────────────────────────────
# TAB 3: INFORMACIÓN
# ─────────────────────────────────────────────────────────
with tab_info:
    st.markdown("### ¿Qué es ContaFlash?")
    st.markdown("""
    **ContaFlash** es una herramienta web gratuita que te permite:

    1. **Extraer datos** de declaraciones PDT 621 (IGV - Renta Mensual) en formato PDF
    2. **Consolidar** múltiples archivos Excel/CSV del PDT en un solo reporte

    #### ¿Cómo funciona?

    **Extracción de PDFs:**
    - Sube tus PDFs de declaraciones SUNAT (o ZIPs con PDFs)
    - La herramienta lee automáticamente todas las casillas del Formulario 621
    - Genera un Excel con una fila por declaración y todas las casillas como columnas
    - Incluye un diccionario de casillas para referencia

    **Consolidación de Excels:**
    - Sube los archivos Excel/CSV exportados del PDT 621
    - La herramienta pivotea las casillas y consolida todo en un reporte
    - Identifica automáticamente declaraciones originales vs. rectificatorias

    #### Casillas soportadas
    Se extraen **+60 casillas** del Formulario 621, incluyendo:
    - IGV Ventas (100-131)
    - IGV Compras (107-178)
    - IVAP (340-341)
    - Renta (301-336)
    - Determinación de deuda (140-324)

    #### Seguridad y privacidad
    - 🔒 Tus archivos se procesan en memoria y **no se almacenan**
    - 🔒 No se guardan datos tributarios ni información sensible
    - 🔒 El procesamiento es temporal — los datos se eliminan al cerrar la página
    """)

    st.markdown("---")
    st.markdown("### Plan Gratuito")
    st.markdown(f"""
    | Característica | Gratuito | Pro |
    |---------------|----------|-----|
    | Procesamientos | {MAX_FREE_USES} por sesión | Ilimitados |
    | Archivos por procesamiento | Sin límite | Sin límite |
    | Formularios soportados | 621 | 621 + más |
    | Soporte | Comunidad | Directo |
    """)

    st.markdown("---")
    st.markdown(
        "Hecho con ❤️ en Perú — "
        "[Contacto](https://wa.me/51962927872?text=Hola%2C+consulta+sobre+ContaFlash) · "
        "© 2026 ContaFlash"
    )

# ─────────────────────────────────────────────────────────
# TAB 4: VALIDACIÓN
# ─────────────────────────────────────────────────────────
with tab_validacion:
    st.markdown("### Resultados de Validación")
    st.markdown(
        "ContaFlash fue probado **en sitio** por contadores reales "
        "realizando tareas reales del día a día."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="validation-metric">
            <div class="number">2</div>
            <div class="label">Contadores evaluados</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="validation-metric">
            <div class="number" style="color:#34d399;">100%</div>
            <div class="label">Tareas completadas</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="validation-metric">
            <div class="number" style="color:#34d399;">0</div>
            <div class="label">Errores encontrados</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Quiénes probaron ContaFlash")

    col_lucy, col_omar = st.columns(2)

    with col_lucy:
        st.markdown("""
        <div class="validation-card">
            <span class="validation-badge">✅ Validado</span>
            <div class="validation-name">Lucy</div>
            <div class="validation-role">Contadora independiente</div>
            <p>Procesó declaraciones PDT 621 reales con PDFs de sus clientes. Extracción exitosa de todas las casillas sin errores.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_omar:
        st.markdown("""
        <div class="validation-card">
            <span class="validation-badge">✅ Validado</span>
            <div class="validation-name">Omar</div>
            <div class="validation-role">Emprendedor / Marketero</div>
            <p>Consolidó múltiples archivos Excel del PDT 621. Verificó que los totales coincidieran con los reportes originales.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ¿Quieres probarlo con tus propios datos?")
    st.markdown(
        "📱 [Escríbenos por WhatsApp](https://wa.me/51962927872?text=Hola%2C+quiero+probar+ContaFlash+con+mis+datos) · "
        "📧 [hola@contaflash.com](mailto:hola@contaflash.com)"
    )
