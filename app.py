"""
ContaFlash — Tus declaraciones en segundos
Web app para extracción y consolidación de declaraciones SUNAT.
"""

import streamlit as st
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
# CONTROL DE USO FREEMIUM (cookie-based via query params)
# ============================================================
MAX_FREE_USES = 3
USAGE_KEY = "contaflash_usage_count"

if USAGE_KEY not in st.session_state:
    st.session_state[USAGE_KEY] = 0


def check_usage() -> bool:
    """Retorna True si el usuario puede usar la herramienta."""
    return st.session_state[USAGE_KEY] < MAX_FREE_USES


def increment_usage():
    """Incrementa el contador de uso."""
    st.session_state[USAGE_KEY] += 1


def remaining_uses() -> int:
    return MAX_FREE_USES - st.session_state[USAGE_KEY]


# ============================================================
# ESTILOS CUSTOM
# ============================================================
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .main-header h1 {
        color: #e67e22;
        font-size: 2.2rem;
    }
    .main-header p {
        color: #566573;
        font-size: 1.1rem;
    }
    .usage-badge {
        background: #f0f3f5;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        text-align: center;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    .stat-card {
        background: #f8f9fa;
        border-left: 4px solid #2ecc71;
        border-radius: 4px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .stat-card.error {
        border-left-color: #e74c3c;
    }
    .block-message {
        text-align: center;
        padding: 2rem;
        background: #fdf2e9;
        border-radius: 12px;
        border: 1px solid #f0b27a;
    }
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


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
if uses_left > 0:
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
tab_pdf, tab_excel, tab_info = st.tabs([
    "📄 Extraer de PDFs",
    "📁 Consolidar Excels",
    "ℹ️ Información"
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
                    excel_bytes, stats, logs = process_uploaded_pdfs(uploaded_pdfs)

                # Mostrar logs
                with st.expander("📋 Detalle del procesamiento", expanded=True):
                    for log_line in logs:
                        st.text(log_line)

                if excel_bytes:
                    increment_usage()

                    # Stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Procesados", f"{stats['ok']}")
                    with col2:
                        st.metric("Errores", f"{stats['errors']}")
                    with col3:
                        n_periodos = len(stats.get('periodos', []))
                        st.metric("Períodos", f"{n_periodos}")

                    if stats.get('periodos'):
                        st.caption(f"Períodos: {', '.join(stats['periodos'])}")

                    # Botón descarga
                    st.download_button(
                        label="📥 Descargar Excel Consolidado",
                        data=excel_bytes,
                        file_name="ContaFlash_621_Consolidado.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                    )
                    st.success(f"✅ Listo — {stats['ok']} declaración(es) extraída(s). Te quedan {remaining_uses()} uso(s) gratuito(s).")
                else:
                    st.error("No se pudieron extraer datos de los archivos proporcionados.")


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
                    excel_bytes, stats, logs = consolidate_uploaded_excels(
                        uploaded_excels, empresa_name
                    )

                with st.expander("📋 Detalle del procesamiento", expanded=True):
                    for log_line in logs:
                        st.text(log_line)

                if excel_bytes:
                    increment_usage()

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Procesados", f"{stats['ok']}")
                    with col2:
                        st.metric("Errores", f"{stats['errors']}")
                    with col3:
                        st.metric("Empresas", f"{stats.get('empresas', 1)}")

                    if stats.get('periodos'):
                        st.caption(f"Períodos: {', '.join(stats['periodos'])}")

                    st.download_button(
                        label="📥 Descargar Consolidado",
                        data=excel_bytes,
                        file_name="ContaFlash_Consolidado_PDT621.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                    )
                    st.success(f"✅ Listo — {stats['ok']} registro(s) consolidado(s). Te quedan {remaining_uses()} uso(s) gratuito(s).")
                else:
                    st.error("No se pudo consolidar. Verifica que los archivos tengan columnas 'Nro Casilla' y 'Valor Casilla'.")


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
