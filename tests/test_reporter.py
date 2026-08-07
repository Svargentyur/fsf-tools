from fsf_core.reporter import PrivacyReporter

def test_reporter_gps_risk():
    reporter = PrivacyReporter()
    metadata = {'gps': {'Latitude': 35.0, 'Longitude': 135.0}}
    risks, score = reporter.analyze(metadata, 'image')
    assert score > 0
    assert any(r['risk_level'] == 'high' for r in risks)

def test_reporter_clean_file():
    reporter = PrivacyReporter()
    metadata = {'basic': {'Format': 'JPEG'}}
    risks, score = reporter.analyze(metadata, 'image')
    assert score == 0
    assert len(risks) == 0

def test_reporter_author_risk():
    reporter = PrivacyReporter()
    metadata = {'info': {'Author': 'Test Author'}}
    risks, score = reporter.analyze(metadata, 'pdf')
    assert score > 0
    assert any(r['field'] == 'Author' for r in risks)
