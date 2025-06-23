import fac as f
import os

def test_create_client():
    client = f.FAC()
    assert client.base == f.FAC_PRODUCTION

def test_create_query():
    client = f.FAC()
    # Params should be alpha sorted by the key.
    client.query("report_id", "eq", "2023-09-GSA-1234")
    client.query("audit_year", "eq", 2023)
    assert client.get_url() == "https://api.fac.gov/general?audit_year=eq.2023&report_id=eq.2023-09-GSA-1234"

def test_chaining():
    client = f.FAC()
    client.query("a", "b", "c").header("a", "b").header("d", "e")
    assert client.get_url() == "https://api.fac.gov/general?a=b.c"
    hs = f.headers_to_dict(client.headers)
    assert sorted(list(hs.keys())) == ["a", "d"]
    assert sorted(list(hs.values())) == ["b", "e"]

def test_fetch_fail():
    client = f.FAC()
    client.param("a", "b")
    client.fetch()
    status = client.error_status()  
    assert status["code"] == "API_KEY_MISSING"

def test_fetch():
    client = f.FAC()
    client.query("audit_year", "eq", 2023)
    client.api_key(os.getenv("FAC_API_KEY"))
    client.fetch()
    assert len(client.results()) > 30_000
