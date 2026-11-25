# Observatorio DIC — TC Perú

Aplicación web académica piloto en Streamlit + Supabase: consulta pública de fichas jurisprudenciales validadas, edición restringida a **dos investigadores**, notas privadas, historial de cambios, carga manual y CSV/XLSX, recuperación controlada de extractos oficiales y consulta IA opcional.

**Para comenzar, lee [GUIA_DESDE_CERO.md](GUIA_DESDE_CERO.md).** No se requiere instalar Python si despliegas con GitHub y Streamlit Community Cloud.

## Carpeta

- `app.py`: interfaz web con consulta pública y área privada.
- `ingest.py`: descarga puntual con respeto de robots, extracción y criba exploratoria.
- `sql/01_esquema_supabase.sql`: tablas, trazabilidad y políticas RLS.
- `requirements.txt`: bibliotecas instaladas por Streamlit Cloud.
- `.streamlit/secrets.toml.example`: nombres de variables, sin credenciales reales.
- `test_ingest.py`: pruebas unitarias simples de extracción/validación.
- `ejemplos/catalogo_piloto_4_casos.csv`: cuatro fichas de prueba con URLs oficiales verificadas; **no** son análisis jurídicos validados.

### Desarrollo local (opcional)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# EDITAR .streamlit/secrets.toml con las dos credenciales reales de Supabase
streamlit run app.py
```

**Atención:** el panel de IA utiliza OpenAI API, no tu sesión personal de ChatGPT. No uses credenciales de administración de Supabase (`service_role`/`sb_secret`) en esta aplicación.

No es una web oficial del Tribunal Constitucional, ni es una recopilación completa de los expedientes. Los registros que aún no han sido verificados permanecen privados.
