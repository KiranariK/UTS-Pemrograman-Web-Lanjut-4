def test_create_incident_success(client,resources):
    u,a=resources
    r=client.post("/api/v1/incidents",json={"title":"Malware terdeteksi","description":"File mencurigakan","incident_type":"malware","severity":"critical","user_id":u,"asset_id":a})
    assert r.status_code==201 and r.get_json()["data"]["severity"]=="critical"
def test_validation_error(client):
    r=client.post("/api/v1/incidents",json={"title":"belum lengkap"})
    assert r.status_code==400 and r.get_json()["success"] is False
def test_search_pagination(client,resources):
    u,a=resources
    client.post("/api/v1/incidents",json={"title":"Phishing email","description":"Email palsu","incident_type":"phishing","user_id":u,"asset_id":a})
    r=client.get("/api/v1/incidents?search=Phishing&page=1&per_page=5")
    assert r.status_code==200 and r.get_json()["meta"]["total"]==1
