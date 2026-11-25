from ingest import validate_tc_url, classify, clean_text

def test_url_official():
    assert validate_tc_url('https://www.tc.gob.pe/jurisprudencia/2026/03269-2023-AA.html')

def test_url_reject_external():
    for u in ('http://www.tc.gob.pe/jurisprudencia/a.pdf',
              'https://evil.example/jurisprudencia/a.pdf',
              'https://www.tc.gob.pe.evil.example/jurisprudencia/a.pdf'):
        try:
            validate_tc_url(u)
        except ValueError:
            continue
        raise AssertionError(u)

def test_classification_is_heuristic():
    x = classify('El derecho antidumping se aplicó a la importación de textiles.')
    assert 'Defensa comercial / OMC' in x
    assert 'Aranceles / aduanas' in x

def test_unaccent():
    assert clean_text('Aráncel') == 'arancel'
