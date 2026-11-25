"""Herramientas de extracción preliminar; no reemplazan el control jurídico."""
from __future__ import annotations

import hashlib
import io
import re
import threading
import time
import unicodedata
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import pandas as pd
import requests
from bs4 import BeautifulSoup

UA = 'ObservatorioDIC-academico/1.0 (respeta robots.txt; contacto: configurar en despliegue)'
_LOCK = threading.Lock()
_LAST_REQUEST = 0.0

PATTERNS = {
    'Defensa comercial / OMC': [r'anti[- ]?dumping', r'derechos? compensatorios?', r'salvaguardias?', r'organizaci[oó]n mundial del comercio'],
    'Aranceles / aduanas': [r'arancel(?:es|ario|aria)?', r'aduan(?:a|as|ero|eros)', r'importaci[oó]n', r'exportaci[oó]n', r'comercio exterior'],
    'MSF / inocuidad': [r'medidas sanitarias y fitosanitarias', r'acuerdo msf', r'codex alimentarius', r'plaguicidas?', r'inocuidad alimentaria'],
    'OTC / normas técnicas': [r'obst[aá]culos t[eé]cnicos al comercio', r'acuerdo otc', r'reglamento t[eé]cnico'],
    'Acuerdos e integración': [r'tratado de libre comercio', r'comunidad andina', r'mercosur', r'acuerdo comercial'],
    'Inversiones / arbitraje': [r'inversi[oó]n extranjera', r'ciadi', r'arbitraje de inversiones', r'tratado bilateral de inversiones'],
    'Logística / contratación': [r'incoterms', r'compraventa internacional', r'transporte internacional de mercanc[ií]as'],
}


def clean_text(text: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', text.lower()) if not unicodedata.combining(c))


def classify(text: str) -> list[str]:
    """Clasificación exploratoria de coincidencias; no determina relevancia DIC."""
    test = clean_text(text or '')
    return [name for name, terms in PATTERNS.items() if any(re.search(clean_text(pat), test, flags=re.I) for pat in terms)]


def validate_tc_url(url: str) -> str:
    value = (url or '').strip()
    p = urlparse(value)
    if (p.scheme != 'https' or p.hostname not in ('tc.gob.pe', 'www.tc.gob.pe')
        or not p.path.startswith('/jurisprudencia/')
        or not re.search(r'\.(html?|pdf)$', p.path, flags=re.I)
        or p.username or p.password):
        raise ValueError('Utiliza una URL directa HTTPS de jurisprudencia en tc.gob.pe (HTML o PDF).')
    return value


def read_table(filename: str, content: bytes) -> pd.DataFrame:
    if filename.lower().endswith('.xlsx'):
        return pd.read_excel(io.BytesIO(content), dtype=str).fillna('')
    if filename.lower().endswith('.csv'):
        for enc in ('utf-8-sig', 'utf-8', 'latin-1'):
            try:
                return pd.read_csv(io.BytesIO(content), dtype=str, encoding=enc, sep=None, engine='python').fillna('')
            except UnicodeDecodeError:
                continue
    raise ValueError('Formato no admitido: utiliza CSV o XLSX.')


def fetch_tc_text(url: str) -> dict:
    """Una descarga manual de texto; respeta robots, espera 30 s y limita tamaño.

    Protege contra redirecciones y dominio no oficial. Un servidor solo, no un
    sistema distribuido de scraping. Para ingesta a escala pedir vía institucional.
    """
    global _LAST_REQUEST
    url = validate_tc_url(url)
    p = urlparse(url)
    robots_url = f'https://{p.hostname}/robots.txt'
    rp = RobotFileParser()
    r = requests.get(robots_url, timeout=15, headers={'User-Agent': UA}, allow_redirects=False)
    r.raise_for_status()
    rp.parse(r.text.splitlines())
    if not rp.can_fetch(UA, url):
        raise PermissionError('robots.txt no permite consultar este enlace.')
    delay = max(30.0, rp.crawl_delay('*') or 0)
    with _LOCK:
        remaining = delay - (time.monotonic() - _LAST_REQUEST)
        if _LAST_REQUEST and remaining > 0:
            time.sleep(remaining)
        _LAST_REQUEST = time.monotonic()
        with requests.get(url, timeout=(10, 55), stream=True, allow_redirects=False,
                          headers={'User-Agent': UA}) as res:
            if 300 <= res.status_code < 400:
                raise ValueError('La fuente redirigió. Verifica el enlace en el TC manualmente.')
            res.raise_for_status()
            content = res.headers.get('Content-Type', '').lower()
            if not any(s in content for s in ('text/html', 'application/pdf', 'application/octet-stream')):
                raise ValueError(f'Formato no admitido: {content}')
            parts, n = [], 0
            for chunk in res.iter_content(65536):
                if chunk:
                    n += len(chunk)
                    if n > 12_000_000:
                        raise ValueError('El documento supera 12 MB.')
                    parts.append(chunk)
        data = b''.join(parts)
    if url.lower().endswith('.pdf') or 'application/pdf' in content:
        import fitz
        with fitz.open(stream=data, filetype='pdf') as doc:
            text = '\n'.join(page.get_text(sort=True) for page in doc)
    else:
        soup = BeautifulSoup(data, 'html.parser')
        for elt in soup(['script', 'style', 'nav', 'footer', 'noscript', 'form']):
            elt.decompose()
        text = (soup.body or soup).get_text(' ', strip=True)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) < 160:
        raise ValueError('No hay texto digital suficiente. Puede necesitar OCR o revisión manual.')
    return {
        'excerpt': text[:40000],
        'characters': len(text),
        'truncated': len(text) > 40000,
        'sha256': hashlib.sha256(text.encode('utf-8')).hexdigest(),
        'suggestions': classify(text),
    }
