"""
Prueba del endpoint de healthcheck y estado del sistema.
"""
def test_healthcheck_endpoint(client):
    r = client.get("/health")
    assert r.status_code == 200
    datos = r.json()
    assert datos["status"] in ("healthy", "degraded")
    assert datos["version"] == "0.7.0"


def test_status_root_endpoint(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "exitosa" in r.json()["mensaje"]
