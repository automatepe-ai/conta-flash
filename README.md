# ⚡ ContaFlash — Tus declaraciones en segundos

Herramienta web para extracción y consolidación de declaraciones SUNAT (Formulario 621 - IGV Renta Mensual).

## Funcionalidades

- **Extraer de PDFs:** Sube PDFs o ZIPs de declaraciones SUNAT → genera Excel consolidado
- **Consolidar Excels:** Sube Excels/CSVs del PDT 621 → consolida en un solo reporte

## Setup local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy en Streamlit Cloud

1. Sube este repo a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repo → branch `main` → archivo `app.py`
4. Deploy automático

## Estructura

```
contaflash/
├── app.py              # Interfaz Streamlit
├── extractor.py        # Motor de extracción (lógica pura)
├── requirements.txt    # Dependencias
├── .streamlit/
│   └── config.toml     # Configuración visual
└── README.md
```
