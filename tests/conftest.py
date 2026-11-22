import pytest
from app import create_app,db
@pytest.fixture()
def app():
    a=create_app({"TESTING":True,"SQLALCHEMY_DATABASE_URI":"sqlite://","SECRET_KEY":"test"})
    with a.app_context():
        db.create_all();yield a;db.session.remove();db.drop_all()
@pytest.fixture()
def client(app):return app.test_client()
@pytest.fixture()
def resources(client):
    u=client.post("/api/v1/users",json={"name":"Tester","email":"test@example.com"}).get_json()["data"]["id"]
    a=client.post("/api/v1/assets",json={"asset_name":"Laptop SOC","asset_type":"endpoint"}).get_json()["data"]["id"]
    return u,a
